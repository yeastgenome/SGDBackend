'''
Created on Feb 19, 2013

@author: kpaskov
'''
from model_new_schema.biorelation import Biorelation
from sgd2.models import DBSession

def weed_out(neighbors, max_count=100):
    if len(neighbors) < max_count:
        return neighbors
    
    evidence_to_neighbors = {}
    for neigh in neighbors:
        evidence_count = neigh.evidence_count
        if evidence_count in evidence_to_neighbors:
            evidence_to_neighbors[evidence_count].append(neigh)
        else:
            evidence_to_neighbors[evidence_count] = [neigh]
            
    sorted_keys = sorted(evidence_to_neighbors.keys(), reverse=True)
    keep = []
    max_evidence_count = max(sorted_keys)
    min_evidence_count = max_evidence_count
    for key in sorted_keys:
        ns = evidence_to_neighbors[key]
        if len(keep) + len(ns) < max_count:
            keep.extend(ns)
            min_evidence_count = key
    return keep, min_evidence_count, max_evidence_count
        
def create_node(obj, evidence_count, focus):
    return {'id':str(obj.id), 'label':obj.name, 'focus':focus, 'link':obj.link, 'evidence':evidence_count}

def create_edge(obj, source_id, sink_id, evidence_count):
    return { 'id': str(obj.id), 'target': source_id, 'source': sink_id, 'label': obj.name, 'link':obj.link, 
            'evidence':evidence_count}  
    
data_schema = {'nodes': [ { 'name': "label", 'type': "string" }, { 'name': "focus", 'type': "string" }, {'name':'link', 'type':'string'}, {'name':'evidence', 'type':'integer'}],
                            'edges': [ { 'name': "label", 'type': "string" }, {'name':'link', 'type':'string'}, {'name':'evidence', 'type':'integer'}]}
    

def create_interaction_graph(bioent):
    
    interactions, min_evidence_count, max_evidence_count = weed_out(bioent.biorelations)
    
    nodes = [create_node(interaction.get_opposite(bioent), interaction.evidence_count, '0') for interaction in interactions]
    nodes.append(create_node(bioent, max_evidence_count, '1'))
    
    node_ids = [int(node['id']) for node in nodes]
    
    interactions = set(DBSession.query(Biorelation).filter(Biorelation.source_bioent_id.in_(node_ids)).all())
    interactions.update(DBSession.query(Biorelation).filter(Biorelation.sink_bioent_id.in_(node_ids)).all())

    edges = []
    for interaction in interactions:
        if interaction.evidence_count >= min_evidence_count and interaction.source_bioent_id in node_ids and interaction.sink_bioent_id in node_ids:
            edges.append(create_edge(interaction, str(interaction.source_bioent_id), str(interaction.sink_bioent_id), interaction.evidence_count))  
        
    return {'dataSchema':data_schema, 'data': {'nodes': nodes, 'edges': edges}, 'evidence_cutoff':min_evidence_count}

    
    
    