'''
Created on May 31, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query.query_bioent import get_bioent_id, get_bioent, get_bioent_from_id
from query.query_evidence import get_bioent_evidence
from query.query_reference import get_reference_id, get_reference_from_id
from sgdbackend.graph_views import create_graph
from sgdbackend.utils import make_reference_list, \
    make_reference_list_order_by_date

@view_config(route_name='bioent_overview_table', renderer='jsonp') 
def bioent_overview_table(request):
    if 'bioent' in request.GET:
        #Need a bioent overview table based on a bioent
        bioent_name = request.GET['bioent']
        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioentevidences = get_bioent_evidence(bioent_id=bioent_id)
        primary_bioentevidences = [evidence for evidence in bioentevidences if evidence.topic=='Primary Literature']
        return make_reference_list(primary_bioentevidences) 
    elif 'reference' in request.GET:
        #Need a bioent overview table based on a reference
        ref_name = request.GET['reference']
        ref_id = get_reference_id(ref_name)
        if ref_id is None:
            return Response(status_int=500, body='Reference could not be found.')
        bioentevidences = get_bioent_evidence(reference_id=ref_id)
        primary = ', '.join([evidence.bioentity.name_with_link for evidence in bioentevidences if evidence.topic=='Primary Literature'])
        additional = ', '.join([evidence.bioentity.name_with_link for evidence in bioentevidences if evidence.topic=='Additional Literature'])
        review = ', '.join([evidence.bioentity.name_with_link for evidence in bioentevidences if evidence.topic=='Reviews'])
        return {'primary': primary, 'additional': additional, 'review': review}
    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')

@view_config(route_name='bioent_evidence_table', renderer='jsonp')
def bioent_evidence_table(request):
    if 'bioent' in request.GET:
        #Need a bioentevidence table based on a bioent
        bioent_name = request.GET['bioent']
        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioentevidences = get_bioent_evidence(bioent_id=bioent_id)
        return make_evidence_table(bioentevidences) 
    else:
        return Response(status_int=500, body='No Bioent specified.')
    
@view_config(route_name='litguide_graph', renderer='jsonp')
def litguide_graph(request):
    if 'bioent' in request.GET:
        #Need a bioentevidence table based on a bioent
        bioent_name = request.GET['bioent']
        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        
        primary_bioentevidences = [x for x in get_bioent_evidence(bioent_id=bioent_id) if x.topic=='Primary Literature']
        return make_litguide_graph(bioent_id, primary_bioentevidences)
        
    else:
        return Response(status_int=500, body='No Bioent specified.')
    
def make_evidence_table(bioentevidences):
    primary_evs = [evidence for evidence in bioentevidences if evidence.topic=='Primary Literature']
    additional_evs = [evidence for evidence in bioentevidences if evidence.topic=='Additional Literature']
    review_evs = [evidence for evidence in bioentevidences if evidence.topic=='Reviews']
    
    tables = {}
    tables['primary'] = make_reference_list_order_by_date(primary_evs) 
    tables['additional'] = make_reference_list_order_by_date(additional_evs) 
    tables['reviews'] = make_reference_list_order_by_date(review_evs) 

    return tables

def create_litguide_bioent_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'LocusNode' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link, 
                    'sub_type':sub_type, 'type': 'BIOENT'}}
    
def create_litguide_ref_node(reference, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'RefNode' + str(reference.id), 'name':reference.display_name, 'link': reference.link, 
                    'sub_type':sub_type, 'type': 'REFERENCE'}}

def create_litguide_edge(bioent_id, reference_id):
    return {'data':{'target': 'LocusNode' + str(bioent_id), 'source': 'RefNode' + str(reference_id)}}

def make_litguide_graph(bioent_id, bioentevidences):
    
    #Get primary genes for each paper in bioentevidences
    reference_ids = set([evidence.reference_id for evidence in bioentevidences])

    reference_id_to_bioent_ids = {}
    for reference_id in reference_ids:
        evs = get_bioent_evidence(reference_id=reference_id)
        bioent_ids = set([x.bioent_id for x in evs if x.topic=='Primary Literature'])
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
    for k, v in top_ref_pairs:
        ref1, ref2 = k
        top_references.add(ref1)
        top_references.add(ref2)
    
    nodes = {}
    nodes_ive_seen = set()
    for reference_id in top_references:
        nodes['Ref' + str(reference_id)] = create_litguide_ref_node(get_reference_from_id(reference_id), False)
        for neigh_id in reference_id_to_bioent_ids[reference_id]:
            if neigh_id in nodes_ive_seen:
                nodes[neigh_id] = create_litguide_bioent_node(get_bioent_from_id(neigh_id), False)
            else:
                nodes_ive_seen.add(neigh_id)
    nodes[bioent_id] = create_litguide_bioent_node(get_bioent_from_id(bioent_id), True)
     
    edges = []           
    for reference_id in top_references:
        for bioent_id in reference_id_to_bioent_ids[reference_id]:
            if bioent_id in nodes:
                edges.append(create_litguide_edge(bioent_id, reference_id))
        
    
    return {'nodes': nodes.values(), 'edges': edges}
    
    
    
