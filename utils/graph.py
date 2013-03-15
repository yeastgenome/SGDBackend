'''
Created on Feb 19, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.biorelation import Biorelation
from sgd2.models import DBSession
from sqlalchemy.orm import joinedload

def weed_out_by_evidence(neighbors, neighbor_evidence_count, max_count=100):
    if len(neighbors) < max_count:
        return neighbors, 1
    
    evidence_to_neighbors = {}
    for neigh in neighbors:
        evidence_count = neighbor_evidence_count[neigh]
        if evidence_count in evidence_to_neighbors:
            evidence_to_neighbors[evidence_count].append(neigh)
        else:
            evidence_to_neighbors[evidence_count] = [neigh]
            
    sorted_keys = sorted(evidence_to_neighbors.keys(), reverse=True)
    keep = []
    min_evidence_count = max(sorted_keys)
    for key in sorted_keys:
        ns = evidence_to_neighbors[key]
        if len(keep) + len(ns) < max_count:
            keep.extend(ns)
            min_evidence_count = key
    return keep, min_evidence_count
        
def create_node(obj, evidence_count, focus_node, sub_type=None):
    if obj == focus_node:
        sub_type = 'FOCUS'
    return {'id':get_id(obj), 'label':obj.name, 'link':obj.link, 'evidence':evidence_count, 'bio_type':obj.type, 'sub_type':sub_type}

def create_go_node(obj, evidence_count, focus_node):
    sub_type = None
    if obj.type == 'BIOCONCEPT':
        sub_type = obj.go_aspect.upper()
    return create_node(obj, evidence_count, focus_node, sub_type)

def create_edge(obj, source_obj, sink_obj, evidence_count):
    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj), 'label': obj.name, 'link':obj.link, 
            'evidence':evidence_count}  
    
data_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'evidence', 'type':'integer'},
                         {'name':'bio_type', 'type':'string'},
                         {'name':'sub_type', 'type':'string'}],
                'edges': [ { 'name': "label", 'type': "string" }, 
                          {'name':'link', 'type':'string'}, 
                          {'name':'evidence', 'type':'integer'}]}
    

def create_interaction_graph(bioent):
        
    bioents = set()
    bioent_to_evidence = {}

    bioents.update([interaction.get_opposite(bioent) for interaction in bioent.biorelations])
    bioent_to_evidence.update([(interaction.get_opposite(bioent), interaction.evidence_count) for interaction in bioent.biorelations])

    bioents.add(bioent)
    max_evidence_cutoff = max(bioent_to_evidence.values())
    bioent_to_evidence[bioent] = max_evidence_cutoff
    
    usable_bioents, min_evidence_count = weed_out_by_evidence(bioents, bioent_to_evidence)
    
    nodes = [create_node(b, bioent_to_evidence[b], bioent) for b in usable_bioents]
    
    node_ids = set([b.id for b in usable_bioents])
    
    interactions = set(DBSession.query(Biorelation).filter(Biorelation.source_bioent_id.in_(node_ids)).all())
    interactions.update(DBSession.query(Biorelation).filter(Biorelation.sink_bioent_id.in_(node_ids)).all())

    edges = []
    for interaction in interactions:
        if interaction.evidence_count >= min_evidence_count and interaction.source_bioent_id in node_ids and interaction.sink_bioent_id in node_ids:
            edges.append(create_edge(interaction, interaction.source_bioent, interaction.sink_bioent, interaction.evidence_count))  
        
    return {'dataSchema':data_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_cutoff}

def get_id(bio):
    return bio.type + str(bio.id)

def create_go_graph(bioent):
        
    bioent_biocons1 = set(DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.biocon_type=='GO').filter(BioentBiocon.bioent_id==bioent.id).filter(BioentBiocon.use_in_graph=='Y').all())

    biocon_ids = [bioent_biocon.biocon_id for bioent_biocon in bioent_biocons1]
    bioent_biocons2 = set(DBSession.query(BioentBiocon).options(joinedload('bioentity'), joinedload('bioconcept')).filter(BioentBiocon.biocon_type=='GO').filter(BioentBiocon.biocon_id.in_(biocon_ids)).filter(BioentBiocon.use_in_graph=='Y').all())
    
    print bioent_biocons1
    usable_bios = set()       
    usable_bios.add(bioent)
    usable_bios.update([bioent_biocon.bioconcept for bioent_biocon in bioent_biocons1])
    
    bio_to_edge_count = {}
    for bioent_biocon in bioent_biocons2:
        b = bioent_biocon.bioentity
        if b in bio_to_edge_count:
            bio_to_edge_count[b] = bio_to_edge_count[b] + 1
        else:
            bio_to_edge_count[b] = 1
       
    more_usable_bios = [bio for bio in bio_to_edge_count.keys() if bio_to_edge_count[bio] > 1]
    
    usable_bios.update(more_usable_bios)
    
        
    nodes = [create_go_node(b, 1, bioent) for b in usable_bios]
    
    edges = []
    for bioent_biocon in bioent_biocons1:
        if bioent_biocon.bioconcept in usable_bios and bioent_biocon.bioentity in usable_bios:
            edges.append(create_edge(bioent_biocon, bioent_biocon.bioentity, bioent_biocon.bioconcept, bioent_biocon.evidence_count))
    
    for bioent_biocon in bioent_biocons2:
        if bioent_biocon.bioconcept in usable_bios and bioent_biocon.bioentity in usable_bios and \
        bioent_biocon.bioentity != bioent:
            edges.append(create_edge(bioent_biocon, bioent_biocon.bioentity, bioent_biocon.bioconcept, bioent_biocon.evidence_count))
    
    
    return {'dataSchema':data_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'min_evidence_cutoff':1, 'max_evidence_cutoff':1}
    
    
    