from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Regulationevidence
import json

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

    return '[' + ', '.join([x.json for x in regevidences if x.json is not None]) + ']'

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, class_type):
    sub_type = class_type
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BIOENTITY' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link, 'type': 'BIOENTITY',
                    'sub_type':sub_type}}

def create_edge(bioent1_id, bioent2_id, total_ev_count, class_type):
    return {'data':{'source': 'BIOENTITY' + str(bioent1_id), 'target': 'BIOENTITY' + str(bioent2_id), 'evidence': total_ev_count, 'action': class_type}}

def make_graph(bioent_id):

    evidences = DBSession.query(Regulationevidence).filter(or_(Regulationevidence.locus1_id == bioent_id, Regulationevidence.locus2_id == bioent_id)).all()
    id_to_neighbor = {}
    edge_key_to_evidence_count = {}
    for evidence in evidences:
        if evidence.direction == 'expression repressed' or evidence.direction == 'expression activated':
            if evidence.locus1_id not in id_to_neighbor:
                id_to_neighbor[evidence.locus1_id] = (evidence.locus1, 'REGULATOR')
            elif id_to_neighbor[evidence.locus1_id][1] == 'TARGET':
                id_to_neighbor[evidence.locus1_id] = (id_to_neighbor[evidence.locus1_id][0], 'BOTH')

            if evidence.locus2_id not in id_to_neighbor:
                id_to_neighbor[evidence.locus2_id] = (evidence.locus2, 'TARGET')
            elif id_to_neighbor[evidence.locus2_id] == 'REGULATOR':
                id_to_neighbor[evidence.locus2_id] = (id_to_neighbor[evidence.locus2_id][0], 'BOTH')

            edge_key = (evidence.locus1_id, evidence.locus2_id, evidence.direction)
            if edge_key in edge_key_to_evidence_count:
                edge_key_to_evidence_count[edge_key] += 1
            else:
                edge_key_to_evidence_count[edge_key] = 1

    neighbor_ids = id_to_neighbor.keys()
    cutoff = 1
    while len(neighbor_ids) > 100:
        cutoff += 1
        edge_key_to_evidence_count = dict([(x, y) for x, y in edge_key_to_evidence_count.iteritems() if y >= cutoff])
        neighbor_ids = set([x[0] for x in edge_key_to_evidence_count.keys()])
        neighbor_ids.update(([x[1] for x in edge_key_to_evidence_count.keys()]))

    id_to_neighbor = dict([(x, y) for x, y in id_to_neighbor.iteritems() if x in neighbor_ids])


    tangent_evidences = DBSession.query(Regulationevidence).filter(and_(Regulationevidence.locus1_id.in_(neighbor_ids), Regulationevidence.locus2_id.in_(neighbor_ids))).all()
    for evidence in tangent_evidences:
        if evidence.locus1_id != bioent_id and evidence.locus2_id != bioent_id and (evidence.direction == 'expression repressed' or evidence.direction == 'expression activated'):
            edge_key = (evidence.locus1_id, evidence.locus2_id, evidence.direction)
            if edge_key in edge_key_to_evidence_count:
                edge_key_to_evidence_count[edge_key] += 1
            else:
                edge_key_to_evidence_count[edge_key] = 1

    edge_key_to_evidence_count = dict([(x, y) for x, y in edge_key_to_evidence_count.iteritems() if y >= cutoff])

    edges = [create_edge(x[0], x[1], y, x[2]) for x, y in edge_key_to_evidence_count.iteritems()]
    nodes = [create_node(x[0], x[0].id==bioent_id, x[1]) for x in id_to_neighbor.values()]

    return {'nodes': nodes, 'edges': edges, 'min_evidence_count': cutoff}
