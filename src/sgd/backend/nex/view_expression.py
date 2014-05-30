from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.evidence import Expressiondata
from sqlalchemy.orm import joinedload
import json
from src.sgd.model.nex.auxiliary import Bioentityinteraction
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.backend.nex.graph_tools import get_interactions_among


__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_expression_evidence(locus_id):
    query = DBSession.query(Expressiondata).options(joinedload('evidence'), joinedload('locus'))
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    expressionevidences = get_expression_evidence(locus_id=locus_id)

    if expressionevidences is None:
        return {'Error': 'Too much data to display.'}

    return json.dumps([x.to_json() for x in expressionevidences])

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BIOENTITY' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'evidence': ev_count,
                    'sub_type':sub_type, 'type': 'BIOENTITY'}}

def create_edge(bioent1_id, bioent2_id, total_ev_count, class_type):
    return {'data':{'target': 'BIOENTITY' + str(bioent1_id), 'source': 'BIOENTITY' + str(bioent2_id),
            'evidence':total_ev_count, 'class_type': class_type}}

def make_graph(bioent_id):
    neighbor_id_to_evidence_count = dict([(x.interactor_id, x.evidence_count) for x in DBSession.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION').filter_by(bioentity_id=bioent_id).all()])
    all_neighbor_ids = set(neighbor_id_to_evidence_count.keys())

    max_count = 0

    evidence_count_to_neighbors = dict()

    for neighbor_id in all_neighbor_ids:
        evidence_count = 0 if neighbor_id not in neighbor_id_to_evidence_count else neighbor_id_to_evidence_count[neighbor_id]

        max_count = max_count if evidence_count <= max_count else evidence_count

        if evidence_count in evidence_count_to_neighbors:
            evidence_count_to_neighbors[evidence_count].add(neighbor_id)
        else:
            evidence_count_to_neighbors[evidence_count] = set([neighbor_id])

    #Apply 100 node cutoff
    min_evidence_count = 100
    usable_neighbor_ids = set()
    while min_evidence_count > 90 and (min_evidence_count not in evidence_count_to_neighbors or (len(usable_neighbor_ids) + len(evidence_count_to_neighbors[min_evidence_count]) < 100)):
        if min_evidence_count in evidence_count_to_neighbors:
            usable_neighbor_ids.update(evidence_count_to_neighbors[min_evidence_count])
        min_evidence_count = min_evidence_count - 1

    print usable_neighbor_ids
    tangent_to_evidence_count = dict([((x.bioentity_id, x.interactor_id), x.evidence_count) for x in get_interactions_among(usable_neighbor_ids, Bioentityinteraction, 'EXPRESSION')])

    evidence_count_to_tangents = dict()

    for tangent, evidence_count in tangent_to_evidence_count.iteritems():
        bioent1_id, bioent2_id = tangent
        if bioent1_id != bioent_id and bioent2_id != bioent_id:
            bioent1_count = 0 if bioent1_id not in neighbor_id_to_evidence_count else neighbor_id_to_evidence_count[bioent1_id]
            bioent2_count = 0 if bioent2_id not in neighbor_id_to_evidence_count else neighbor_id_to_evidence_count[bioent2_id]

            index = min(bioent1_count, bioent2_count, evidence_count)
            if index in evidence_count_to_tangents:
                evidence_count_to_tangents[index].add(tangent)
            else:
                evidence_count_to_tangents[index] = set([tangent])

    #Apply 250 edge cutoff
    old_min_evidence_count = min_evidence_count
    min_evidence_count = 100
    edges = []
    nodes = [create_node(DBSession.query(Bioentity).filter_by(id=bioent_id).first(), True, max_count-90)]
    min_evidence_used = 100
    while min_evidence_count > 90 and ((len(edges) + (0 if min_evidence_count not in evidence_count_to_neighbors else len(evidence_count_to_neighbors[min_evidence_count])) + (0 if min_evidence_count not in evidence_count_to_tangents else len(evidence_count_to_tangents[min_evidence_count]))< 250 and min_evidence_count > old_min_evidence_count)):
        if min_evidence_count in evidence_count_to_neighbors:
            for neighbor_id in evidence_count_to_neighbors[min_evidence_count]:
                count = 0 if neighbor_id not in neighbor_id_to_evidence_count else neighbor_id_to_evidence_count[neighbor_id]
                nodes.append(create_node(DBSession.query(Bioentity).filter_by(id=neighbor_id).first(), False, count))
                if count < min_evidence_used:
                    min_evidence_used = count

            if min_evidence_count in evidence_count_to_neighbors:
                for genetic_id in evidence_count_to_neighbors[min_evidence_count]:
                    edges.append(create_edge(bioent_id, genetic_id, min_evidence_count, ''))

            if min_evidence_count in evidence_count_to_tangents:
                for tangent in evidence_count_to_tangents[min_evidence_count]:
                    bioent1_id, bioent2_id = tangent
                    if bioent1_id < bioent2_id:
                        edges.append(create_edge(bioent1_id, bioent2_id, min_evidence_count, ''))

        min_evidence_count = min_evidence_count - 1

    return {'nodes': nodes, 'edges': edges,
            'min_evidence_cutoff':min_evidence_used, 'max_evidence_cutoff':max_count}
