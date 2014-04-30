from sqlalchemy import or_, and_

from src.sgd.backend.nex import DBSession, query_limit, link_gene_names
from src.sgd.backend.nex.query_tools import get_paragraph
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Regulationevidence

# -------------------------------Paragraph---------------------------------------
def make_paragraph(bioent_id):
    paragraph = get_paragraph(bioent_id, 'REGULATION')

    if paragraph is None:
        return None

    paragraph_json = paragraph.to_json()
    bioentity = paragraph.bioentity
    to_ignore = {bioentity.format_name, bioentity.display_name, bioentity.format_name + 'P', bioentity.display_name + 'P'}
    paragraph_json['text'] = link_gene_names(paragraph.text, to_ignore=to_ignore)
    return paragraph_json

# -------------------------------Evidence Table---------------------------------------
def get_regulation_evidence(locus_id, reference_id, between_ids):
    query = DBSession.query(Regulationevidence)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if between_ids is not None:
        query = query.filter(and_(Regulationevidence.locus1_id.in_(between_ids), Regulationevidence.locus2_id.in_(between_ids)))
    if locus_id is not None:
        query = query.filter(or_(Regulationevidence.locus1_id == locus_id, Regulationevidence.locus2_id == locus_id))

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, reference_id=None):
    if locus_id is None and reference_id is None:
        return {'Error': 'No locus_id or reference_id given.'}

    regevidences = get_regulation_evidence(locus_id=locus_id, reference_id=reference_id, between_ids=None)

    if regevidences is None:
        return {'Error': 'Too much data to display.'}

    return [x.to_json() for x in regevidences]

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, targ_ev_count, reg_ev_count, class_type):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link, 'class_type': class_type,
                    'sub_type':sub_type, 'targ_evidence': targ_ev_count, 'reg_evidence': reg_ev_count, 'evidence': max(targ_ev_count, reg_ev_count)}}

def create_edge(bioent1_id, bioent2_id, total_ev_count, class_type):
    return {'data':{'source': 'Node' + str(bioent1_id), 'target': 'Node' + str(bioent2_id), 'evidence': total_ev_count, 'class_type': class_type}}
    
def make_graph(bioent_id):
    #Test getting rid of Venters
    evidences = get_regulation_evidence(locus_id=bioent_id, reference_id=None, between_ids=None)
    regulator_id_to_evidence_count = {}
    target_id_to_evidence_count = {}
    for evidence in evidences:
        if evidence.locus2_id == bioent_id:
            if evidence.locus1_id in regulator_id_to_evidence_count:
                regulator_id_to_evidence_count[evidence.locus1_id] = regulator_id_to_evidence_count[evidence.locus1_id] + 1
            else:
                regulator_id_to_evidence_count[evidence.locus1_id] = 1
        elif evidence.locus1_id == bioent_id:
            if evidence.locus2_id in target_id_to_evidence_count:
                target_id_to_evidence_count[evidence.locus2_id] = target_id_to_evidence_count[evidence.locus2_id] + 1
            else:
                target_id_to_evidence_count[evidence.locus2_id] = 1
    #neighbor_interactions = get_interactions('REGULATION', bioent_id=bioent_id)
    
    #regulator_id_to_evidence_count = dict([(x.bioentity1_id, x.evidence_count) for x in neighbor_interactions if x.bioentity2_id==bioent_id])
    #target_id_to_evidence_count = dict([(x.bioentity2_id, x.evidence_count) for x in neighbor_interactions if x.bioentity1_id==bioent_id])

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

    #Test getting rid of Venters
    evidences = get_regulation_evidence(locus_id=None, reference_id=None, between_ids=usable_neighbor_ids)
    tangent_to_evidence_count = {}
    for evidence in evidences:
        if (evidence.locus1_id, evidence.locus2_id) in tangent_to_evidence_count:
            tangent_to_evidence_count[(evidence.locus1_id, evidence.locus2_id)] = tangent_to_evidence_count[(evidence.locus1_id, evidence.locus2_id)] + 1
        else:
            tangent_to_evidence_count[(evidence.locus1_id, evidence.locus2_id)] = 1
    #tangent_to_evidence_count = dict([((x.bioentity1_id, x.bioentity2_id), x.evidence_count) for x in get_interactions_among('REGULATION', usable_neighbor_ids, min_evidence_count)])
    
    evidence_count_to_tangents = [set() for _ in range(11)]
    
    for tangent, evidence_count in tangent_to_evidence_count.iteritems():
        if evidence_count >= min_evidence_count:
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
    nodes = [create_node(DBSession.query(Bioentity).filter_by(id=bioent_id).first(), True, max_target_count, max_regulator_count, 'FOCUS')]
    accepted_neighbor_ids = set()
    while len(edges) + len(evidence_count_to_targets[min_evidence_count]) + len(evidence_count_to_regulators[min_evidence_count]) + len(evidence_count_to_tangents[min_evidence_count]) < 250 and min_evidence_count > old_min_evidence_count:
        accepted_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        
        for regulator_id in evidence_count_to_regulators[min_evidence_count]:
            regevidence_count = regulator_id_to_evidence_count[regulator_id]
            if regulator_id != bioent_id:
                edges.append(create_edge(regulator_id, bioent_id, regevidence_count, 'REGULATOR'))
            else:
                edges.append(create_edge(regulator_id, bioent_id, regevidence_count, 'BOTH'))
            
        for target_id in evidence_count_to_targets[min_evidence_count]:
            targevidence_count = target_id_to_evidence_count[target_id]
            if target_id != bioent_id:
                edges.append(create_edge(bioent_id, target_id, targevidence_count, 'TARGET'))
            
        for tangent in evidence_count_to_tangents[min_evidence_count]:
            bioent1_id, bioent2_id = tangent
            evidence_count = tangent_to_evidence_count[tangent]
            edges.append(create_edge(bioent1_id, bioent2_id, evidence_count, 'BOTH'))
            
        min_evidence_count = min_evidence_count - 1
        
    for neighbor in DBSession.query(Bioentity).filter(Bioentity.id.in_(accepted_neighbor_ids)).all():
        neighbor_id = neighbor.id
        regevidence_count = 0 if neighbor_id not in regulator_id_to_evidence_count else regulator_id_to_evidence_count[neighbor_id]
        targevidence_count = 0 if neighbor_id not in target_id_to_evidence_count else target_id_to_evidence_count[neighbor_id]
        node_type = 'BOTH'
        if regevidence_count <= min_evidence_count:
            node_type = 'TARGET'
        if targevidence_count <= min_evidence_count:
            node_type = 'REGULATOR'
        nodes.append(create_node(neighbor, False, targevidence_count, regevidence_count, node_type))
    
    return {'nodes': nodes, 'edges': edges, 
            'min_evidence_cutoff':min_evidence_count+1, 'max_evidence_cutoff':max_union_count,
            'max_target_cutoff': max_target_count, 'max_regulator_cutoff': max_regulator_count}
