'''
Created on Sep 20, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Domainevidence, Phosphorylationevidence
from sgdbackend_query import get_evidence
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_bioitem
from sgdbackend_utils.obj_to_json import minimize_json, evidence_to_json

# -------------------------------Overview---------------------------------------
def make_overview(protein_id):
    return id_to_bioent[protein_id]

'''
-------------------------------Details---------------------------------------
''' 
def make_details(protein_id=None, reference_id=None, domain_id=None):
    domain_evidences = get_evidence(Domainevidence, bioent_id=protein_id, reference_id=reference_id, bioitem_id=domain_id)
    if domain_evidences is None:
        return {'Error': 'Too much data to display.'}

    domain_evidences = [x for x in domain_evidences if x.domain.display_name != 'seg' ]
    return create_simple_table(domain_evidences, make_evidence_row) 

def make_evidence_row(domain_evidence): 
    obj_json = evidence_to_json(domain_evidence).copy()
    obj_json['protein'] = id_to_bioent[domain_evidence.bioentity_id]
    obj_json['domain'] = id_to_bioitem[domain_evidence.bioitem_id]
    obj_json['start'] = domain_evidence.start
    obj_json['end'] = domain_evidence.end
    obj_json['evalue'] = domain_evidence.evalue
    obj_json['status'] = domain_evidence.status
    obj_json['date_of_run'] = domain_evidence.date_of_run
    return obj_json

'''
-------------------------------Details---------------------------------------
'''
def make_phosphorylation_details(protein_id=None):
    phospho_evidences = get_evidence(Phosphorylationevidence, bioent_id=protein_id)
    if phospho_evidences is None:
        return {'Error': 'Too much data to display.'}

    return create_simple_table(sorted(phospho_evidences, key=lambda x: x.site_index), make_phospho_evidence_row)

def make_phospho_evidence_row(phospho_evidence):
    obj_json = evidence_to_json(phospho_evidence).copy()
    obj_json['protein'] = id_to_bioent[phospho_evidence.bioentity_id]
    obj_json['site_index'] = phospho_evidence.site_index
    obj_json['site_residue'] = phospho_evidence.site_residue
    return obj_json

# -------------------------------Graph-----------------------------------------

def create_bioent_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'],
                    'sub_type':sub_type, 'type': 'BIOENTITY'}}

def create_domain_node(bioitem):
    return {'data':{'id':'DomainNode' + str(bioitem['id']), 'name':bioitem['display_name'], 'link': bioitem['link'],
                    'sub_type':None, 'type': 'BIOITEM'}}

def create_edge(bioent_id, domain_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'DomainNode' + str(domain_id)}}

def make_graph(protein_id):

    #Get domains for protein
    domain_ids = set([x.bioitem_id for x in get_evidence(Domainevidence, bioent_id=protein_id) if x.domain.display_name != 'seg' ])
    unique_domains = []

    domain_id_to_bioent_ids = {}
    bioent_id_to_domain_ids = {}

    all_relevant_edges = set()
    for domain_id in domain_ids:
        domain_domainevidences = get_evidence(Domainevidence, bioitem_id=domain_id)
        all_relevant_edges.update([(x.bioentity_id, x.bioitem_id) for x in domain_domainevidences if x.domain.display_name != 'seg' ])
        if len(set([x.bioentity_id for x in domain_domainevidences])) == 1:
            unique_domains.extend([make_evidence_row(x) for x in domain_domainevidences])

    for edge in all_relevant_edges:
        bioentity_id = edge[0]
        domain_id = edge[1]

        if domain_id in domain_id_to_bioent_ids:
            domain_id_to_bioent_ids[domain_id].add(bioentity_id)
        else:
            domain_id_to_bioent_ids[domain_id] = set([bioentity_id])

        if bioentity_id in bioent_id_to_domain_ids:
            bioent_id_to_domain_ids[bioentity_id].add(domain_id)
        else:
            bioent_id_to_domain_ids[bioentity_id] = set([domain_id])

    cutoff = 1
    node_count = len(bioent_id_to_domain_ids) + len(domain_id_to_bioent_ids)
    edge_count = len(all_relevant_edges)
    bioent_count = len(bioent_id_to_domain_ids)
    domain_ids_in_use = set([x for x, y in domain_id_to_bioent_ids.iteritems()])
    bioent_ids_in_use = set([x for x, y in bioent_id_to_domain_ids.iteritems()])
    edges_in_use = [x for x in all_relevant_edges]
    while node_count > 100 or edge_count > 250 or bioent_count > 50:
        cutoff = cutoff + 1
        bioent_ids_in_use = set([x for x, y in bioent_id_to_domain_ids.iteritems() if len(y) >= cutoff])
        domain_ids_in_use = set([x for x, y in domain_id_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
        edges_in_use = [x for x in all_relevant_edges if x[0] in bioent_ids_in_use and x[1] in domain_ids_in_use]
        node_count = len(bioent_ids_in_use) + len(domain_ids_in_use)
        edge_count = len(edges_in_use)
        bioent_count = len(bioent_ids_in_use)

    if len(bioent_ids_in_use) > 0:

        bioent_to_score = dict({(x, len(y&domain_ids_in_use)) for x, y in bioent_id_to_domain_ids.iteritems()})
        bioent_to_score[protein_id] = 0

        nodes = [create_bioent_node(id_to_bioent[x], x==protein_id) for x in bioent_ids_in_use]
        nodes.extend([create_domain_node(id_to_bioitem[x]) for x in domain_ids_in_use])

        edges = [create_edge(evidence[0], evidence[1]) for evidence in edges_in_use]

        return {'nodes': nodes, 'edges': edges, 'max_cutoff': max(bioent_to_score.values()), 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x != protein_id]), 'unique_domains':unique_domains}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0, 'unique_domains':unique_domains}