'''
Created on Mar 15, 2013

@author: kpaskov
'''
from sgdbackend_query import get_evidence
from sgdbackend_query.query_auxiliary import get_interactions, \
    get_interactions_among
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_reference, \
    id_to_experiment, id_to_strain, id_to_biocon, id_to_source
from sgdbackend_utils.obj_to_json import minimize_bioent_json, \
    minimize_reference_json, minimize_experiment_json, minimize_strain_json, \
    minimize_biocon_json
from sgdbackend_utils.venn import calc_venn_measurements

'''
-------------------------------Overview---------------------------------------
'''  

def make_overview(bioent):
    genetic = get_interactions('GENINTERACTION', bioent['id'])
    physical = get_interactions('PHYSINTERACTION', bioent['id'])
            
    inters_to_genetic = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in genetic])
    inters_to_physical = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in physical])
               
    all_inters = set(inters_to_genetic.keys())
    all_inters.update(inters_to_physical.keys())
    
    A = 0
    B = 0
    C = 0
    for inter in all_inters:
        gen = inter in inters_to_genetic
        phys = inter in inters_to_physical
        if gen:
            A = A+1
        if phys:
            B = B+1
        if gen and phys:
            C = C+1
            
    r, s, x = calc_venn_measurements(A, B, C)
    
    return {'gen_circle_size': r, 'phys_circle_size':s, 'circle_distance': x, 
            'num_gen_interactors': A, 'num_phys_interactors': B, 'num_both_interactors': C}

    
'''
-------------------------------Details---------------------------------------
'''
    
def make_details(divided, bioent_id):
    from model_new_schema.evidence import Geninteractionevidence, Physinteractionevidence
    genetic_interevidences = get_evidence(Geninteractionevidence, bioent_id=bioent_id)
    physical_interevidences = get_evidence(Physinteractionevidence, bioent_id=bioent_id)
            
    tables = {}

    all_interevidences = [x for x in genetic_interevidences]
    all_interevidences.extend(physical_interevidences)

    if divided:
        tables['genetic'] = create_simple_table(genetic_interevidences, make_evidence_row, bioent_id=bioent_id)
        tables['physical'] = create_simple_table(physical_interevidences, make_evidence_row, bioent_id=bioent_id)
        
    else:
        tables = create_simple_table(all_interevidences, make_evidence_row, bioent_id=bioent_id)
        
    return tables  

def make_evidence_row(interevidence, bioent_id=None): 
    if bioent_id is not None:
        if interevidence.bioentity1_id == bioent_id:
            bioent1_id = bioent_id
            bioent2_id = interevidence.bioentity2_id
            direction = interevidence.bait_hit.split('-').pop(1)
        else:
            bioent1_id = bioent_id
            bioent2_id = interevidence.bioentity1_id
            direction = interevidence.bait_hit.split('-').pop(0)
    else:
        bioent1_id = interevidence.bioentity1_id
        bioent2_id = interevidence.bioentity2_id
        direction = interevidence.bait_hit

    reference_id = interevidence.reference_id 
    experiment_id = interevidence.experiment_id
    strain_id = interevidence.strain_id
    note=interevidence.note
    source = id_to_source[interevidence.source_id]
        
    if interevidence.class_type == 'GENINTERACTION':
        phenotype_id = interevidence.phenotype_id
        return {'bioent1': minimize_bioent_json(id_to_bioent[bioent1_id]),
                'bioent2': minimize_bioent_json(id_to_bioent[bioent2_id]),
                'interaction_type': 'Genetic',
                'reference': None if reference_id is None else minimize_reference_json(id_to_reference[reference_id]),
                'experiment': None if experiment_id is None else minimize_experiment_json(id_to_experiment[experiment_id]),
                'strain': None if strain_id is None else minimize_strain_json(id_to_strain[strain_id]),
                'phenotype': None if phenotype_id is None else minimize_biocon_json(id_to_biocon[phenotype_id]),
                'annotation_type': interevidence.annotation_type,
                'direction': direction,
                'source': source,
                'note': note
                }
        
    elif interevidence.class_type == 'PHYSINTERACTION':
        return {'bioent1': minimize_bioent_json(id_to_bioent[bioent1_id]),
                'bioent2': minimize_bioent_json(id_to_bioent[bioent2_id]),
                'interaction_type': 'Physical',
                'reference': None if reference_id is None else minimize_reference_json(id_to_reference[reference_id]),
                'experiment': None if experiment_id is None else minimize_experiment_json(id_to_experiment[experiment_id]),
                'strain': None if strain_id is None else minimize_strain_json(id_to_strain[strain_id]),
                'modification': interevidence.modification,
                'annotation_type': interevidence.annotation_type,
                'direction': direction,
                'source': source,
                'note': note
                }
        
    else:
        return None

'''
-------------------------------Graph---------------------------------------
'''  

def create_node(bioent, is_focus, gen_ev_count, phys_ev_count, total_ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'], 
                    'physical': phys_ev_count, 'genetic': gen_ev_count, 'evidence':total_ev_count, 
                    'sub_type':sub_type}}

def create_edge(interaction_id, bioent1_id, bioent2_id, gen_ev_count, phys_ev_count, total_ev_count):
    return {'data':{'target': 'Node' + str(bioent1_id), 'source': 'Node' + str(bioent2_id), 
            'physical': phys_ev_count, 'genetic': gen_ev_count, 'evidence':total_ev_count}}
    
def make_graph(bioent_id):
    neighbor_id_to_genevidence_count = dict([(x.bioentity1_id if x.bioentity2_id==bioent_id else x.bioentity2_id, x.evidence_count) for x in get_interactions('GENSINTERACTION', bioent_id)])
    neighbor_id_to_physevidence_count = dict([(x.bioentity1_id if x.bioentity2_id==bioent_id else x.bioentity2_id, x.evidence_count) for x in get_interactions('PHYSINTERACTION', bioent_id)])
    all_neighbor_ids = set()
    all_neighbor_ids.update(neighbor_id_to_genevidence_count.keys())
    all_neighbor_ids.update(neighbor_id_to_physevidence_count.keys())
    
    max_union_count = 0
    max_phys_count = 0
    max_gen_count = 0
    max_intersect_count = 0
    
    evidence_count_to_neighbors = [set() for _ in range(11)]
    
    for neighbor_id in all_neighbor_ids:
        genevidence_count = min(10, 0 if neighbor_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[neighbor_id])
        physevidence_count = min(10, 0 if neighbor_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[neighbor_id])
        gen_and_phys = min(10, genevidence_count + physevidence_count)
        min_gen_phys = min(genevidence_count, physevidence_count)
        
        max_gen_count = max_gen_count if genevidence_count <= max_gen_count else genevidence_count
        max_phys_count = max_phys_count if physevidence_count <= max_phys_count else physevidence_count
        max_union_count = max_union_count if gen_and_phys <= max_union_count else gen_and_phys
        max_intersect_count = max_intersect_count if min_gen_phys <= max_intersect_count else min_gen_phys
        
        evidence_count_to_neighbors[gen_and_phys].add(neighbor_id)
        
    #Apply 100 node cutoff
    min_evidence_count = 10
    usable_neighbor_ids = {}
    while len(usable_neighbor_ids) + len(evidence_count_to_neighbors[min_evidence_count]) < 100 and min_evidence_count > 1:
        usable_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        min_evidence_count = min_evidence_count - 1
      
    tangent_to_genevidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('GENINTERACTION', usable_neighbor_ids, min_evidence_count)])
    tangent_to_physevidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('PHYSINTERACTION', usable_neighbor_ids, min_evidence_count)])
    tangents = set()
    tangents.update(tangent_to_genevidence_count.keys())
    tangents.update(tangent_to_physevidence_count.keys())
    
    evidence_count_to_tangents = [set() for _ in range(11)]
    
    for tangent in tangents:
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:
            genevidence_count = 0 if tangent not in tangent_to_genevidence_count else tangent_to_genevidence_count[tangent]
            physevidence_count = 0 if tangent not in tangent_to_physevidence_count else tangent_to_physevidence_count[tangent]
        
            gen_and_phys = min(10, genevidence_count + physevidence_count)
            bioent1_count = 0 if bioent1_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent1_id] + \
                            0 if bioent1_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent1_id]
            bioent2_count = 0 if bioent2_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[bioent2_id] + \
                            0 if bioent2_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[bioent2_id]
            
            index = min(bioent1_count, bioent2_count, gen_and_phys)
            evidence_count_to_tangents[index].add(tangent)
        
    #Apply 250 edge cutoff
    old_min_evidence_count = min_evidence_count
    min_evidence_count = 10
    edges = []
    nodes = [create_node(id_to_bioent[bioent_id], True, max_gen_count, max_phys_count, max_union_count)]
    while len(edges) + len(evidence_count_to_neighbors[min_evidence_count]) + (evidence_count_to_tangents[min_evidence_count]) < 250 and min_evidence_count > old_min_evidence_count:
        for neighbor_id in evidence_count_to_neighbors[min_evidence_count]:
            gen_ev_count = 0 if neighbor_id not in neighbor_id_to_genevidence_count else neighbor_id_to_genevidence_count[neighbor_id]
            phys_ev_count = 0 if neighbor_id not in neighbor_id_to_physevidence_count else neighbor_id_to_physevidence_count[neighbor_id]
            nodes.append(create_node(id_to_bioent[neighbor_id], False, gen_ev_count, phys_ev_count, gen_ev_count+phys_ev_count))
            edges.append(create_edge(len(edges), neighbor_id, bioent1_id, gen_ev_count, phys_ev_count, gen_ev_count + phys_ev_count))
            
        for tangent in evidence_count_to_tangents:
            bioent1_id, bioent2_id = tangent
            gen_ev_count = 0 if tangent not in tangent_to_genevidence_count else tangent_to_genevidence_count[tangent]
            phys_ev_count = 0 if tangent not in tangent_to_physevidence_count else tangent_to_physevidence_count[tangent]
            edges.append(create_edge(len(edges), bioent1_id, bioent2_id, gen_ev_count, phys_ev_count, gen_ev_count + phys_ev_count))
            
        min_evidence_count = min_evidence_count - 1
    
    return {'nodes': nodes, 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_union_count,
            'max_phys_cutoff': max_phys_count, 'max_gen_cutoff': max_gen_count, 'max_both_cutoff': max_intersect_count}


