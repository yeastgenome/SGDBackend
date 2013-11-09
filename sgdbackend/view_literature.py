'''
Created on May 31, 2013

@author: kpaskov
'''

from sgdbackend_query.query_auxiliary import get_bioentity_references
from sgdbackend_utils import make_references
from sgdbackend_utils.cache import id_to_reference, id_to_bioent
  
'''
-------------------------------Overview---------------------------------------
'''   

def make_overview(bioent_id):
    references = {}
    references['primary'] = make_references(['PRIMARY_LITERATURE'], bioent_id) 
    references['total_count'] = len(set([x.reference_id for x in get_bioentity_references(bioent_id=bioent_id)]))
    return references

'''
-------------------------------Details---------------------------------------
'''   

def make_details(bioent_id):
    references = {}
    references['primary'] = make_references(['PRIMARY_LITERATURE'], bioent_id) 
    references['additional'] = make_references(['ADDITIONAL_LITERATURE'], bioent_id) 
    references['reviews'] = make_references(['REVIEW_LITERATURE'], bioent_id) 
    references['go'] = make_references(['GO'], bioent_id, only_primary=True) 
    references['phenotype'] = make_references(['PHENOTYPE'], bioent_id, only_primary=True) 
    references['interaction'] = make_references(['GENINTERACTION', 'PHYSINTERACTION'], bioent_id) 
    references['regulation'] = make_references(['REGULATION'], bioent_id) 
    return references

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

def make_graph(bioent_id):
    
    #Get primary genes for each paper in bioentevidences
    reference_ids = [x.reference_id for x in get_bioentity_references('PRIMARY_LITERATURE', bioent_id=bioent_id)]

    reference_id_to_bioent_ids = {}
    for bioent_ref in get_bioentity_references('PRIMARY_LITERATURE', reference_ids=reference_ids):
        bioentity_id = bioent_ref.bioentity_id
        reference_id = bioent_ref.reference_id
        if reference_id in reference_id_to_bioent_ids:
            reference_id_to_bioent_ids[reference_id].add(bioentity_id)
        else:
            reference_id_to_bioent_ids[reference_id] = set([bioentity_id])
     
    #Calculate weight between every pair of papers
    reference_pair_to_weight = {}
    for reference_id1 in reference_ids:
        for reference_id2 in reference_ids:
            if reference_id1 < reference_id2:
                bioent_ids1 = reference_id_to_bioent_ids[reference_id1]
                bioent_ids2 = reference_id_to_bioent_ids[reference_id2]
                overlap = bioent_ids1 & bioent_ids2
                overlap_len = len(overlap)
                if overlap_len > 1 and len(bioent_ids2) <= 10 and len(bioent_ids2) <= 10:
                    weight = 1.0*overlap_len*overlap_len*overlap_len/(len(bioent_ids1)*len(bioent_ids2))
                    reference_pair_to_weight[reference_id1, reference_id2] = weight
                
    #Find papers with top 20 weights.
    max_num = 15
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
        nodes['Ref' + str(reference_id)] = create_litguide_ref_node(id_to_reference[reference_id], False)
        for neigh_id in reference_id_to_bioent_ids[reference_id]:
            if neigh_id in nodes_ive_seen:
                nodes[neigh_id] = create_litguide_bioent_node(id_to_bioent[neigh_id], False)
            else:
                nodes_ive_seen.add(neigh_id)
    nodes[bioent_id] = create_litguide_bioent_node(id_to_bioent[bioent_id], True)
     
    edges = []           
    for reference_id in top_references:
        for bioent_id in reference_id_to_bioent_ids[reference_id]:
            if bioent_id in nodes:
                edges.append(create_litguide_edge(bioent_id, reference_id))
        
    
    return {'nodes': nodes.values(), 'edges': edges}
    
    
    