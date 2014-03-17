from sqlalchemy import or_

from src.sgd.backend.nex import create_simple_table, DBSession, query_limit
from src.sgd.backend.nex.query_tools import get_paragraph, get_interactions, get_conditions, get_interactions_among
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Regulationevidence
from src.sgd.backend.nex.cache import get_obj
from src.sgd.backend.nex.obj_to_json import paragraph_to_json, condition_to_json, \
    minimize_json, evidence_to_json


# -------------------------------Overview---------------------------------------
def make_overview(bioent_id):
    overview = {}
    interactions = get_interactions('REGULATION', bioent_id)
    target_count = len([interaction.bioentity2_id for interaction in interactions if interaction.bioentity1_id==bioent_id])
    regulator_count = len([interaction.bioentity1_id for interaction in interactions if interaction.bioentity2_id==bioent_id])
    
    overview['target_count'] = target_count
    overview['regulator_count'] = regulator_count
    return overview

# -------------------------------Paragraph---------------------------------------
def make_paragraph(bioent_id):
    paragraph = get_paragraph(bioent_id, 'REGULATION')
    return None if paragraph is None else paragraph_to_json(paragraph)

# -------------------------------Evidence Table---------------------------------------
def get_regulation_evidence(locus_id, reference_id):
    query = DBSession.query(Regulationevidence)
    if locus_id is not None:
        query = query.filter(or_(Regulationevidence.bioentity1_id == locus_id, Regulationevidence.bioentity2_id == locus_id))
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, reference_id=None):
    if locus_id is None and reference_id is None:
        return {'Error': 'No locus_id or reference_id given.'}

    regevidences = get_regulation_evidence(locus_id=locus_id, reference_id=reference_id)

    if regevidences is None:
        return {'Error': 'Too much data to display.'}

    id_to_conditions = {}
    for condition in get_conditions([x.id for x in regevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]

    return create_simple_table(regevidences, make_evidence_row, id_to_conditions=id_to_conditions)

def make_evidence_row(regevidence, id_to_conditions): 
    conditions = [] if regevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[regevidence.id]]
        
    obj_json = evidence_to_json(regevidence).copy()
    obj_json['bioentity1'] = minimize_json(get_obj(Bioentity, regevidence.bioentity1_id), include_format_name=True)
    obj_json['bioentity2'] = minimize_json(get_obj(Bioentity, regevidence.bioentity2_id), include_format_name=True)
    obj_json['conditions'] = conditions
    return obj_json

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, targ_ev_count, reg_ev_count, class_type):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'], 'class_type': class_type,
                    'sub_type':sub_type, 'targ_evidence': targ_ev_count, 'reg_evidence': reg_ev_count, 'evidence': max(targ_ev_count, reg_ev_count)}}

def create_edge(interaction_id, bioent1_id, bioent2_id, total_ev_count, class_type):
    return {'data':{'source': 'Node' + str(bioent1_id), 'target': 'Node' + str(bioent2_id), 'evidence': total_ev_count, 'class_type': class_type}}
    
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
    evidence_count_to_targets = [set() for _ in range(11)]
    evidence_count_to_regulators = [set() for _ in range(11)]
    
    for neighbor_id in all_neighbor_ids:        
        regevidence_count = min(10, 0 if neighbor_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[neighbor_id])
        targevidence_count = min(10, 0 if neighbor_id not in target_id_to_evidence_count else target_id_to_evidence_count[neighbor_id])
        reg_and_targ = min(10, max(regevidence_count, targevidence_count))
        
        max_target_count = max_target_count if targevidence_count <= max_target_count else targevidence_count
        max_regulator_count = max_regulator_count if regevidence_count <= max_regulator_count else regevidence_count
        max_union_count = max_union_count if reg_and_targ <= max_union_count else reg_and_targ
        
        evidence_count_to_targets[targevidence_count].add(neighbor_id)
        evidence_count_to_regulators[regevidence_count].add(neighbor_id)
        evidence_count_to_neighbors[reg_and_targ].add(neighbor_id)
        
    #Apply 100 node cutoff
    min_evidence_count = 10
    usable_neighbor_ids = set()
    while len(usable_neighbor_ids) + len(evidence_count_to_neighbors[min_evidence_count]) < 100 and min_evidence_count > 1:
        usable_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        min_evidence_count = min_evidence_count - 1
      
    tangent_to_evidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('REGULATION', usable_neighbor_ids, min_evidence_count)])
    
    evidence_count_to_tangents = [set() for _ in range(11)]
    
    for tangent, evidence_count in tangent_to_evidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:        
            bioent1_count = max(0 if bioent1_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[bioent1_id],
                            0 if bioent1_id not in target_id_to_evidence_count else target_id_to_evidence_count[bioent1_id])
            bioent2_count = max(0 if bioent2_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[bioent2_id],
                            0 if bioent2_id not in target_id_to_evidence_count else target_id_to_evidence_count[bioent2_id])
            
            index = min(10, bioent1_count, bioent2_count, evidence_count)
            evidence_count_to_tangents[index].add(tangent)
    
    #Apply 250 edge cutoff
    old_min_evidence_count = min_evidence_count
    min_evidence_count = 10
    edges = []
    nodes = [create_node(get_obj(Bioentity, bioent_id), True, max_target_count, max_regulator_count, 'FOCUS')]
    accepted_neighbor_ids = set()
    while len(edges) + len(evidence_count_to_targets[min_evidence_count]) + len(evidence_count_to_regulators[min_evidence_count]) + len(evidence_count_to_tangents[min_evidence_count]) < 250 and min_evidence_count > old_min_evidence_count:
        accepted_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        
        for regulator_id in evidence_count_to_regulators[min_evidence_count]:
            regevidence_count = regulator_id_to_evidence_count[regulator_id]
            if regulator_id != bioent_id:
                edges.append(create_edge(len(edges), regulator_id, bioent_id, regevidence_count, 'REGULATOR'))
            else:
                edges.append(create_edge(len(edges), regulator_id, bioent_id, regevidence_count, 'BOTH'))
            
        for target_id in evidence_count_to_targets[min_evidence_count]:
            targevidence_count = target_id_to_evidence_count[target_id]
            if target_id != bioent_id:
                edges.append(create_edge(len(edges), bioent_id, target_id, targevidence_count, 'TARGET'))
            
        for tangent in evidence_count_to_tangents[min_evidence_count]:
            bioent1_id, bioent2_id = tangent
            evidence_count = tangent_to_evidence_count[tangent]
            edges.append(create_edge(len(edges), bioent1_id, bioent2_id, evidence_count, 'BOTH'))
            
        min_evidence_count = min_evidence_count - 1
        
    for neighbor_id in accepted_neighbor_ids:
        regevidence_count = 0 if neighbor_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[neighbor_id]
        targevidence_count = 0 if neighbor_id not in target_id_to_evidence_count else target_id_to_evidence_count[neighbor_id]
        node_type = 'BOTH'
        if regevidence_count <= min_evidence_count:
            node_type = 'TARGET'
        if targevidence_count <= min_evidence_count:
            node_type = 'REGULATOR'
        nodes.append(create_node(get_obj(Bioentity, neighbor_id), False, targevidence_count, regevidence_count, node_type))
    
    return {'nodes': nodes, 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count+1, 'max_evidence_cutoff':max_union_count,
            'max_target_cutoff': max_target_count, 'max_regulator_cutoff': max_regulator_count}
