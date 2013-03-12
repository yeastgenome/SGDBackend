'''
Created on Feb 19, 2013

@author: kpaskov
'''
from model_new_schema.biorelation import Biorelation
from sgd2.models import DBSession

def create_graph(bioent):
    nodes = []
    edges = []
        
    neighbor_ids = set()
    neighbor_ids.add(bioent.id)
    
    two_evidence_neighbors = []
    two_evidence_neighbor_ids = set()
    one_evidence_neighbors = []
    one_evidence_neighbor_ids = set()

    max_evidence_count = 0;
    for interaction in bioent.biorelations:
        if interaction.evidence_count > 2:
            node_list = nodes
            node_ids = neighbor_ids
        elif interaction.evidence_count == 2:
            node_list = two_evidence_neighbors
            node_ids = two_evidence_neighbor_ids
        else:
            node_list = one_evidence_neighbors
            node_ids = one_evidence_neighbor_ids
            
        if interaction.source_bioent_id == bioent.id:
            neighbor = interaction.sink_bioent
        else:
            neighbor = interaction.source_bioent
            
        node_list.append({'id':str(neighbor.id), 'label':neighbor.name, 'focus':'0', 'link':neighbor.link, 'evidence':interaction.evidence_count})
        node_ids.add(neighbor.id)
        if interaction.evidence_count > max_evidence_count:
            max_evidence_count = interaction.evidence_count
        
    evidence_cutoff = 3
    if len(neighbor_ids) + len(two_evidence_neighbor_ids) < 100:
        neighbor_ids.update(two_evidence_neighbor_ids)
        nodes.extend(two_evidence_neighbors)      
        evidence_cutoff = 2
        
    if len(neighbor_ids) + len(one_evidence_neighbor_ids) < 100:
        neighbor_ids.update(one_evidence_neighbor_ids)
        nodes.extend(one_evidence_neighbors) 
        evidence_cutoff = 1
                
    nodes.append({'id':str(bioent.id), 'label':bioent.name, 'focus':'1', 'link':bioent.link, 'evidence':max_evidence_count})
    
        
    interactions = set(DBSession.query(Biorelation).filter(Biorelation.source_bioent_id.in_(neighbor_ids)).all())
    interactions.update(DBSession.query(Biorelation).filter(Biorelation.sink_bioent_id.in_(neighbor_ids)).all())

    for interaction in interactions:
        if interaction.evidence_count >= evidence_cutoff and interaction.source_bioent_id in neighbor_ids and interaction.sink_bioent_id in neighbor_ids:
            edges.append({ 'id': str(interaction.id), 'target': str(interaction.source_bioent_id), 'source': str(interaction.sink_bioent_id), 'label': interaction.name, 'link':interaction.link, 'evidence':interaction.evidence_count})      
        
    graph = {'dataSchema': {'nodes': [ { 'name': "label", 'type': "string" }, { 'name': "focus", 'type': "string" }, {'name':'link', 'type':'string'}, {'name':'evidence', 'type':'integer'}],
                            'edges': [ { 'name': "label", 'type': "string" }, {'name':'link', 'type':'string'}, {'name':'evidence', 'type':'integer'}]},
            'data': {'nodes': nodes, 'edges': edges}, 'evidence_cutoff':evidence_cutoff}
    return graph
    