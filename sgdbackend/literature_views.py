'''
Created on May 31, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend_query.query_reference import get_references
from sgdbackend.cache import get_cached_bioent, get_cached_reference
from sgdbackend.utils import make_reference_list

@view_config(route_name='literature_overview', renderer='jsonp') 
def literature_overview(request):
    #Need a bioent overview table based on a bioent
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')  
    return make_reference_list(['PRIMARY_LIT_EVIDENCE'], bioent['id']) 

@view_config(route_name='literature_details', renderer='jsonp')
def literature_details(request):
    #Need a bioentevidence table based on a bioent
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    references = {}
    references['primary'] = make_reference_list(['PRIMARY_LIT_EVIDENCE'], bioent['id']) 
    references['additional'] = make_reference_list(['ADDITIONAL_LIT_EVIDENCE'], bioent['id']) 
    references['reviews'] = make_reference_list(['REVIEW_LIT_EVIDENCE'], bioent['id'])  
    return references 
    
@view_config(route_name='literature_graph', renderer='jsonp')
def literature_graph(request):
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.') 
    return make_litguide_graph(bioent['id'])
    

'''
-------------------------------Graph---------------------------------------
'''  

def create_litguide_bioent_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'LocusNode' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'], 
                    'sub_type':sub_type, 'type': 'BIOENT'}}
    
def create_litguide_ref_node(reference, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'RefNode' + str(reference['id']), 'name':reference['display_name'], 'link': reference['link'], 
                    'sub_type':sub_type, 'type': 'REFERENCE'}}

def create_litguide_edge(bioent_id, reference_id):
    return {'data':{'target': 'LocusNode' + str(bioent_id), 'source': 'RefNode' + str(reference_id)}}

def make_litguide_graph(bioent_id):
    
    #Get primary genes for each paper in bioentevidences
    reference_ids = [x.reference_id for x in get_references('PRIMARY_LIT_EVIDENCE', bioent_id=bioent_id)]

    reference_id_to_bioent_ids = {}
    for reference_id in reference_ids:
        bioent_ids = set([x.bioent_id for x in get_references('PRIMARY_LIT_EVIDENCE', reference_id=reference_id)])
        reference_id_to_bioent_ids[reference_id] = bioent_ids
     
    #Calculate weight between every pair of papers
    reference_pair_to_weight = {}
    for reference_id1 in reference_ids:
        for reference_id2 in reference_ids:
            if reference_id1 < reference_id2:
                bioent_ids1 = reference_id_to_bioent_ids[reference_id1]
                bioent_ids2 = reference_id_to_bioent_ids[reference_id2]
                overlap = bioent_ids1 & bioent_ids2
                overlap_len = len(overlap)
                if overlap_len > 1:
                    weight = 1.0*overlap_len*overlap_len*overlap_len/(len(bioent_ids1)*len(bioent_ids2))
                    reference_pair_to_weight[reference_id1, reference_id2] = weight
                
    #Find papers with top 20 weights.
    max_num = 20
    top_ref_pairs = []

    for ref_pair, weight in reference_pair_to_weight.iteritems():
        if len(top_ref_pairs) < max_num:
            top_ref_pairs.append((ref_pair, weight))
        elif weight > top_ref_pairs[0][1]:
            top_ref_pairs.pop()
            top_ref_pairs.append((ref_pair, weight))
        top_ref_pairs.sort(key=lambda k:k[1])
    
    top_references = set()
    for pair in top_ref_pairs:
        ref1, ref2 = pair[0]
        top_references.add(ref1)
        top_references.add(ref2)
    
    nodes = {}
    nodes_ive_seen = set()
    for reference_id in top_references:
        nodes['Ref' + str(reference_id)] = create_litguide_ref_node(get_cached_reference(reference_id), False)
        for neigh_id in reference_id_to_bioent_ids[reference_id]:
            if neigh_id in nodes_ive_seen:
                nodes[neigh_id] = create_litguide_bioent_node(get_cached_bioent(neigh_id), False)
            else:
                nodes_ive_seen.add(neigh_id)
    nodes[bioent_id] = create_litguide_bioent_node(get_cached_bioent(bioent_id), True)
     
    edges = []           
    for reference_id in top_references:
        for bioent_id in reference_id_to_bioent_ids[reference_id]:
            if bioent_id in nodes:
                edges.append(create_litguide_edge(bioent_id, reference_id))
        
    
    return {'nodes': nodes.values(), 'edges': edges}
    
    
    