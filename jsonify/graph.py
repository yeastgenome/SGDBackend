'''
Created on Feb 19, 2013

@author: kpaskov
'''
from jsonify.mini import bioent_mini
from jsonify.small import biorel_small
from model_new_schema.biorelation import Biorelation
from sgd2.models import DBSession

def create_graph(bioent):
    nodes = []
    edges = []
    
    bioent_id = str(bioent.id)
    bioent_json = bioent_mini(bioent)
    nodes.append({'id':str(bioent_id), 'label':str(bioent_json['name']), 'focus':'1', 'link':str(bioent_json['link'])})
    
    neighbor_ids = set()
    neighbor_ids.add(bioent.id)

    for interaction in bioent.biorelations:
        if interaction.evidence_count > 2:
            if interaction.source_bioent_id == bioent.id:
                neighbor = interaction.sink_bioent
            else:
                neighbor = interaction.source_bioent
            
            if not neighbor.id in neighbor_ids:
                neighbor_json = bioent_mini(neighbor)
                nodes.append({'id':str(neighbor.id), 'label':str(neighbor_json['name']), 'focus':'0', 'link':str(neighbor_json['link'])})
                neighbor_ids.add(neighbor.id)
        
    interactions = set(DBSession.query(Biorelation).filter(Biorelation.source_bioent_id.in_(neighbor_ids)).all())
    interactions.update(DBSession.query(Biorelation).filter(Biorelation.sink_bioent_id.in_(neighbor_ids)).all())

    for interaction in interactions:
        if interaction.evidence_count > 2 and interaction.source_bioent_id in neighbor_ids and interaction.sink_bioent_id in neighbor_ids:
            edges.append({ 'id': str(interaction.id), 'target': str(interaction.source_bioent_id), 'source': str(interaction.sink_bioent_id), 'label': str(interaction.name), 'link':'/biorel/' + str(interaction.name)})      
        
    graph = {'dataSchema': {'nodes': [ { 'name': "label", 'type': "string" }, { 'name': "focus", 'type': "string" }, {'name':'link', 'type':'string'}],
                            'edges': [ { 'name': "label", 'type': "string" }, {'name':'link', 'type':'string'}]},
            'data': {'nodes': nodes, 'edges': edges}}
    return graph
    