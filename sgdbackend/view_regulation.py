'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Regulationevidence
from sgdbackend_query import get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_interactions, \
    get_interactions_among
from sgdbackend_query.query_paragraph import get_paragraph
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_reference, \
    id_to_experiment, id_to_strain, id_to_source
from sgdbackend_utils.obj_to_json import paragraph_to_json, condition_to_json
 
'''
-------------------------------Overview---------------------------------------
'''
def make_overview(bioent_id):
    overview = {}
    paragraph = get_paragraph(bioent_id, 'REGULATION')
    if paragraph is not None:
        overview['paragraph'] = paragraph_to_json(paragraph)
    interactions = get_interactions('REGULATION', bioent_id)
    target_count = len([interaction.bioentity2_id for interaction in interactions if interaction.bioentity1_id==bioent_id])
    regulator_count = len([interaction.bioentity1_id for interaction in interactions if interaction.bioentity2_id==bioent_id])
    
    overview['target_count'] = target_count
    overview['regulator_count'] = regulator_count
    return overview
   
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_details(divided, bioent_id):
    regevidences = get_evidence(Regulationevidence, bioent_id=bioent_id)
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in regevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
            
    tables = {}

    if divided:
        target_regevidences = [regevidence for regevidence in regevidences if regevidence.bioentity1_id==bioent_id]
        regulator_regevidences = [regevidence for regevidence in regevidences if regevidence.bioentity2_id==bioent_id]
        
        tables['targets'] = create_simple_table(target_regevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        tables['regulators'] = create_simple_table(regulator_regevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    else:
        tables = create_simple_table(regevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    return tables    

def minimize_bioent_json(bioent_json):
    if bioent_json is not None:
        return {'display_name': bioent_json['display_name'],
            'format_name': bioent_json['format_name'],
            'link': bioent_json['link']}
    return None
    
def minimize_reference_json(ref_json):
    if ref_json is not None:
        return {'display_name': ref_json['display_name'],
            'link': ref_json['link']}
    return None
    
def minimize_strain_json(strain_json):
    if strain_json is not None:
        return {'display_name': strain_json['display_name'],
            'link': strain_json['link']}
    return None
    
def minimize_experiment_json(exp_json):
    if exp_json is not None:
        return {'display_name': exp_json['display_name'],
            'link': exp_json['link']}
    return None

def make_evidence_row(regevidence, id_to_conditions): 
    reference_id = regevidence.reference_id 
    experiment_id = regevidence.experiment_id
    strain_id = regevidence.strain_id
    
    conditions = None if regevidence.id not in id_to_conditions else ';'.join(condition_to_json(x) for x in id_to_conditions[regevidence.id])
        
    return {'bioent1': minimize_bioent_json(id_to_bioent[regevidence.bioentity1_id]),
                'bioent2': minimize_bioent_json(id_to_bioent[regevidence.bioentity2_id]),
                'reference': None if reference_id is None else minimize_reference_json(id_to_reference[reference_id]),
                'experiment': None if experiment_id is None else minimize_experiment_json(id_to_experiment[experiment_id]),
                'strain': None if strain_id is None else minimize_strain_json(id_to_strain[strain_id]),
                'source': id_to_source[regevidence.source_id],
                'conditions': conditions
                }

'''
-------------------------------Graph---------------------------------------
'''  

def create_node(bioent, is_focus, total_ev_count, class_type):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'], 
                    'sub_type':sub_type, 'evidence': total_ev_count, 'class_type': class_type}}

def create_edge(interaction_id, bioent1_id, bioent2_id, total_ev_count):
    return {'data':{'source': 'Node' + str(bioent1_id), 'target': 'Node' + str(bioent2_id), 'evidence': total_ev_count}}
    
def make_graph(bioent_id):
    neighbor_interactions = get_interactions('REGULATION', bioent_id=bioent_id)
    
    regulator_id_to_evidence_count = dict([(x.bioentity1_id, x.evidence_count) for x in neighbor_interactions if x.bioentity2_id==bioent_id])
    target_id_to_evidence_count = dict([(x.bioentity2_id, x.evidence_count) for x in neighbor_interactions if x.bioentity1_id==bioent_id])
    all_neighbor_ids = set()
    all_neighbor_ids.update(regulator_id_to_evidence_count.keys())
    all_neighbor_ids.update(target_id_to_evidence_count.keys())
    
    max_union_count = 0
    max_target_count = 0
    max_regulator_count = 0
    
    evidence_count_to_neighbors = [set() for _ in range(11)]
    
    for neighbor_id in all_neighbor_ids:        
        regevidence_count = min(10, 0 if neighbor_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[neighbor_id])
        targevidence_count = min(10, 0 if neighbor_id not in target_id_to_evidence_count else target_id_to_evidence_count[neighbor_id])
        reg_and_targ = min(10, regevidence_count + regevidence_count)
        
        max_target_count = max_target_count if targevidence_count <= max_target_count else targevidence_count
        max_regulator_count = max_regulator_count if regevidence_count <= max_regulator_count else regevidence_count
        max_union_count = max_union_count if reg_and_targ <= max_union_count else reg_and_targ
        
        evidence_count_to_neighbors[reg_and_targ].add(neighbor_id)
        
    #Apply 100 node cutoff
    min_evidence_count = 10
    usable_neighbor_ids = {}
    while len(usable_neighbor_ids) + len(evidence_count_to_neighbors[min_evidence_count]) < 100 and min_evidence_count > 1:
        usable_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        min_evidence_count = min_evidence_count - 1
      
    tangent_to_evidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('REGULATION', usable_neighbor_ids, min_evidence_count)])
    
    evidence_count_to_tangents = [set() for _ in range(11)]
    
    for tangent, evidence_count in tangent_to_evidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:        
            bioent1_count = 0 if bioent1_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[bioent1_id] + \
                            0 if bioent1_id not in target_id_to_evidence_count else target_id_to_evidence_count[bioent1_id]
            bioent2_count = 0 if bioent2_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[bioent2_id] + \
                            0 if bioent2_id not in target_id_to_evidence_count else target_id_to_evidence_count[bioent2_id]
            
            index = min(bioent1_count, bioent2_count, evidence_count)
            evidence_count_to_tangents[index].add(tangent)
    
    #Apply 250 edge cutoff
    old_min_evidence_count = min_evidence_count
    min_evidence_count = 10
    edges = []
    nodes = [create_node(id_to_bioent[bioent_id], True, max_union_count, 'FOCUS')]
    while len(edges) + len(evidence_count_to_neighbors[min_evidence_count]) + (evidence_count_to_tangents[min_evidence_count]) < 250 and min_evidence_count > old_min_evidence_count:
        for neighbor_id in evidence_count_to_neighbors[min_evidence_count]:
            regevidence_count = 0 if neighbor_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[neighbor_id]
            targevidence_count = 0 if neighbor_id not in target_id_to_evidence_count else target_id_to_evidence_count[neighbor_id]
            nodes.append(create_node(id_to_bioent[neighbor_id], False, max(regevidence_count + targevidence_count), 'REGULATOR' if regevidence_count > targevidence_count else 'TARGET'))
            if regevidence_count > 0:
                edges.append(create_edge(len(edges), neighbor_id, bioent1_id, regevidence_count))
            if targevidence_count > 0:
                edges.append(create_edge(len(edges), bioent1_id, neighbor_id, targevidence_count))
            
        for tangent in evidence_count_to_tangents:
            bioent1_id, bioent2_id = tangent
            evidence_count = tangent_to_evidence_count[tangent]
            edges.append(create_edge(len(edges), bioent1_id, bioent2_id, evidence_count))
            
        min_evidence_count = min_evidence_count - 1
    
    return {'nodes': nodes, 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_union_count,
            'max_target_cutoff': max_target_count, 'max_regulator_cutoff': max_regulator_count}

