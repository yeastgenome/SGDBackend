'''
Created on May 31, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Literatureevidence
from sgdbackend_query import get_evidence

from sgdbackend_query.query_auxiliary import get_bioentity_references
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_reference, id_to_bioent
from sgdbackend_utils.obj_to_json import evidence_to_json, minimize_json

'''
-------------------------------Overview---------------------------------------
'''   

def make_overview(bioent_id):
    references = {}

    primary_ids = set([x.reference_id for x in get_bioentity_references('PRIMARY_LITERATURE', bioent_id=bioent_id)])
    all_ids = set(primary_ids)
    all_ids.update([x.reference_id for x in get_bioentity_references('PRIMARY_LITERATURE', bioent_id=bioent_id)])
    all_ids.update([x.reference_id for x in get_bioentity_references('ADDITIONAL_LITERATURE', bioent_id=bioent_id)])
    all_ids.update([x.reference_id for x in get_bioentity_references('REVIEW_LITERATURE', bioent_id=bioent_id)])
    all_ids.update([x.reference_id for x in get_bioentity_references('GO', bioent_id=bioent_id) if x.reference_id in primary_ids])
    all_ids.update([x.reference_id for x in get_bioentity_references('PHENOTYPE', bioent_id=bioent_id) if x.reference_id in primary_ids])
    all_ids.update([x.reference_id for x in get_bioentity_references('GENINTERACTION', bioent_id=bioent_id)])
    all_ids.update([x.reference_id for x in get_bioentity_references('PHYSINTERACTION', bioent_id=bioent_id)])
    all_ids.update([x.reference_id for x in get_bioentity_references('REGULATION', bioent_id=bioent_id)])

    references['total_count'] = len(all_ids)
    return references

'''
-------------------------------Details---------------------------------------
'''   

def make_details(locus_id=None, reference_id=None):
    if locus_id is not None and reference_id is None:
        references = {}
        references['primary'] = make_references(['PRIMARY_LITERATURE'], locus_id)
        references['additional'] = make_references(['ADDITIONAL_LITERATURE'], locus_id)
        references['reviews'] = make_references(['REVIEW_LITERATURE'], locus_id)
        references['go'] = make_references(['GO'], locus_id, only_primary=True)
        references['phenotype'] = make_references(['PHENOTYPE'], locus_id, only_primary=True)
        references['interaction'] = make_references(['GENINTERACTION', 'PHYSINTERACTION'], locus_id)
        references['regulation'] = make_references(['REGULATION'], locus_id)
        return references
    else:
        evidences = get_evidence(Literatureevidence, bioent_id=locus_id, reference_id=reference_id);
        if evidences is None:
            return {'Error': 'Too much data to display.'}
        tables = {}
        tables['primary'] = create_simple_table([x for x in evidences if x.topic == 'Primary Literature'], make_evidence_row)
        tables['additional'] = create_simple_table([x for x in evidences if x.topic == 'Additional Literature'], make_evidence_row)
        tables['reviews'] = create_simple_table([x for x in evidences if x.topic == 'Reviews'], make_evidence_row)
        return tables

def make_references(bioent_ref_types, bioent_id, only_primary=False):
    from sgdbackend_query.query_auxiliary import get_bioentity_references
    reference_ids = set()
    for bioent_ref_type in bioent_ref_types:
        reference_ids.update([x.reference_id for x in get_bioentity_references(bioent_ref_type, bioent_id=bioent_id)])

    if only_primary:
        primary_ids = set([x.reference_id for x in get_bioentity_references('PRIMARY_LITERATURE', bioent_id=bioent_id)])
        reference_ids.intersection_update(primary_ids)

    references = [id_to_reference[reference_id] for reference_id in reference_ids]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True)
    return references

def make_evidence_row(litevidence):
    bioentity_id = litevidence.bioentity_id

    obj_json = evidence_to_json(litevidence).copy()
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['topic'] = litevidence.topic
    return obj_json

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
    
'''
-------------------------------Snapshot---------------------------------------
'''
def make_snapshot():
    snapshot = {}
    return snapshot
