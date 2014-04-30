from sqlalchemy import or_

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.backend.nex.graph_tools import get_interactions_among
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence
from src.sgd.model.nex.auxiliary import Bioentityinteraction


__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_genetic_interaction_evidence(locus_id, reference_id):
    query = DBSession.query(Geninteractionevidence)
    if locus_id is not None:
        query = query.filter(or_(Geninteractionevidence.locus1_id == locus_id, Geninteractionevidence.locus2_id == locus_id))
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_physical_interaction_evidence(locus_id, reference_id):
    query = DBSession.query(Physinteractionevidence)
    if locus_id is not None:
        query = query.filter(or_(Physinteractionevidence.locus1_id == locus_id, Physinteractionevidence.locus2_id == locus_id))
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, reference_id=None):
    if locus_id is None and reference_id is None:
        return {'Error': 'No locus_id or reference_id given.'}

    genetic_interevidences = get_genetic_interaction_evidence(locus_id=locus_id, reference_id=reference_id)
    physical_interevidences = get_physical_interaction_evidence(locus_id=locus_id, reference_id=reference_id)

    if genetic_interevidences is None or physical_interevidences is None:
        return {'Error': 'Too much data to display.'}

    all_interevidences = [x for x in genetic_interevidences]
    all_interevidences.extend(physical_interevidences)

    return [x.to_json() for x in all_interevidences]

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, gen_ev_count, phys_ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'physical': phys_ev_count, 'genetic': gen_ev_count, 'evidence':max(phys_ev_count, gen_ev_count), 
                    'sub_type':sub_type}}

def create_edge(bioent1_id, bioent2_id, total_ev_count, class_type):
    return {'data':{'target': 'Node' + str(bioent1_id), 'source': 'Node' + str(bioent2_id), 
            'evidence':total_ev_count, 'class_type': class_type}}
    
def make_graph(bioent_id):
    neighbor_id_to_genevidence_count = dict([(x.interactor_id, x.evidence_count) for x in DBSession.query(Bioentityinteraction).filter_by(interaction_type='GENINTERACTION').filter_by(bioentity_id=bioent_id).all()])
    neighbor_id_to_physevidence_count = dict([(x.interactor_id, x.evidence_count) for x in DBSession.query(Bioentityinteraction).filter_by(interaction_type='PHYSINTERACTION').filter_by(bioentity_id=bioent_id).all()])
    all_neighbor_ids = set()
    all_neighbor_ids.update(neighbor_id_to_genevidence_count.keys())
    all_neighbor_ids.update(neighbor_id_to_physevidence_count.keys())
    
    max_union_count = 0
    max_phys_count = 0
    max_gen_count = 0
    
    evidence_count_to_neighbors = [set() for _ in range(11)]
    evidence_count_to_genetic = [set() for _ in range(11)]
    evidence_count_to_physical = [set() for _ in range(11)]
    
    for neighbor_id in all_neighbor_ids:
        genevidence_count = min(10, 0 if neighbor_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[neighbor_id])
        physevidence_count = min(10, 0 if neighbor_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[neighbor_id])
        gen_and_phys = min(10, max(genevidence_count, physevidence_count))
        
        max_gen_count = max_gen_count if genevidence_count <= max_gen_count else genevidence_count
        max_phys_count = max_phys_count if physevidence_count <= max_phys_count else physevidence_count
        max_union_count = max_union_count if gen_and_phys <= max_union_count else gen_and_phys
        
        evidence_count_to_neighbors[gen_and_phys].add(neighbor_id)
        evidence_count_to_genetic[genevidence_count].add(neighbor_id)
        evidence_count_to_physical[physevidence_count].add(neighbor_id)
        
    #Apply 100 node cutoff
    min_evidence_count = 10
    usable_neighbor_ids = set()
    while len(usable_neighbor_ids) + len(evidence_count_to_neighbors[min_evidence_count]) < 100 and min_evidence_count > 1:
        usable_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        min_evidence_count = min_evidence_count - 1
      
    tangent_to_genevidence_count = dict([((x.bioentity_id, x.interactor_id), x.evidence_count) for x in get_interactions_among(usable_neighbor_ids, Bioentityinteraction, 'GENINTERACTION')])
    tangent_to_physevidence_count = dict([((x.bioentity_id, x.interactor_id), x.evidence_count) for x in get_interactions_among(usable_neighbor_ids, Bioentityinteraction, 'PHYSINTERACTION')])
    
    evidence_count_to_phys_tangents = [set() for _ in range(11)]
    evidence_count_to_gen_tangents = [set() for _ in range(11)]
    
    for tangent, evidence_count in tangent_to_genevidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:
            bioent1_count = max(0 if bioent1_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent1_id],
                            0 if bioent1_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent1_id])
            bioent2_count = max(0 if bioent2_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent2_id],
                            0 if bioent2_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent2_id])
            
            index = min(10, bioent1_count, bioent2_count, evidence_count)
            evidence_count_to_gen_tangents[index].add(tangent)
            
    for tangent, evidence_count in tangent_to_physevidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:
            bioent1_count = max(0 if bioent1_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent1_id],
                            0 if bioent1_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent1_id])
            bioent2_count = max(0 if bioent2_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent2_id],
                            0 if bioent2_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent2_id])
            
            index = min(10, bioent1_count, bioent2_count, evidence_count)
            evidence_count_to_phys_tangents[index].add(tangent)
        
    #Apply 250 edge cutoff
    old_min_evidence_count = min_evidence_count
    min_evidence_count = 10
    edges = []
    nodes = [create_node(DBSession.query(Bioentity).filter_by(id=bioent_id).first(), True, max_gen_count, max_phys_count)]
    while len(edges) + len(evidence_count_to_physical[min_evidence_count]) + len(evidence_count_to_genetic[min_evidence_count]) + len(evidence_count_to_phys_tangents[min_evidence_count]) + len(evidence_count_to_gen_tangents[min_evidence_count]) < 250 and min_evidence_count > old_min_evidence_count:
        for neighbor_id in evidence_count_to_neighbors[min_evidence_count]:
            physical_count = 0 if neighbor_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[neighbor_id]
            genetic_count = 0 if neighbor_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[neighbor_id]
            nodes.append(create_node(DBSession.query(Bioentity).filter_by(id=neighbor_id).first(), False, genetic_count, physical_count))
        
        for genetic_id in evidence_count_to_genetic[min_evidence_count]:
            genevidence_count = neighbor_id_to_genevidence_count[genetic_id]
            edges.append(create_edge(bioent_id, genetic_id, genevidence_count, 'GENETIC'))
                
        for physical_id in evidence_count_to_physical[min_evidence_count]:
            physevidence_count = neighbor_id_to_physevidence_count[physical_id]
            edges.append(create_edge(bioent_id, physical_id, physevidence_count, 'PHYSICAL'))
        
        for tangent in evidence_count_to_gen_tangents[min_evidence_count]:
            bioent1_id, bioent2_id = tangent
            gen_ev_count = tangent_to_genevidence_count[tangent]
            edges.append(create_edge(bioent1_id, bioent2_id, gen_ev_count, 'GENETIC'))
            
        for tangent in evidence_count_to_phys_tangents[min_evidence_count]:
            bioent1_id, bioent2_id = tangent
            phys_ev_count = tangent_to_physevidence_count[tangent]
            edges.append(create_edge(bioent1_id, bioent2_id, phys_ev_count, 'PHYSICAL'))
            
        min_evidence_count = min_evidence_count - 1
    
    return {'nodes': nodes, 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count+1, 'max_evidence_cutoff':max_union_count,
            'max_phys_cutoff': max_phys_count, 'max_gen_cutoff': max_gen_count}