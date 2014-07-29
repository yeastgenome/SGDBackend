from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.model.nex.evidence import Bioentitydata
from sqlalchemy.orm import joinedload
import json
from src.sgd.model.nex.auxiliary import Bioentityinteraction
from src.sgd.model.nex.bioentity import Locus
from src.sgd.backend.nex.graph_tools import get_interactions_among
from src.sgd.model.nex.evidence import Expressionevidence
from src.sgd.model.nex.bioitem import Datasetcolumn
from decimal import Decimal

__author__ = 'kpaskov'

# -------------------------------Details---------------------------------------
def get_expression_evidence(locus_id, evidence_id):
    query = DBSession.query(Bioentitydata).options(joinedload(Bioentitydata.evidence))
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if evidence_id is not None:
        query = query.filter_by(evidence_id=evidence_id)

    return query.all()

def make_details(locus_id=None, datasetcolumn_id=None):
    if locus_id is None and datasetcolumn_id is None:
        return {'Error': 'No locus_id or datasetcolumn_id given.'}

    evidence = None
    if datasetcolumn_id is not None:
        evidence = DBSession.query(Expressionevidence).filter_by(datasetcolumn_id=datasetcolumn_id).options(joinedload(Expressionevidence.datasetcolumn)).first()

    expressionevidences = get_expression_evidence(locus_id=locus_id, evidence_id=None if evidence is None else evidence.id)

    if locus_id is not None:
        #Expression
        id_to_datasetcolumn = dict([(x.id, x) for x in DBSession.query(Datasetcolumn).options(joinedload(Datasetcolumn.dataset)).all()])
        expression_collapsed = {}
        sum = 0;
        sum_of_squares = 0;
        n = 0;
        id_to_dataset = dict()
        for x in expressionevidences:
            dataset = id_to_datasetcolumn[x.evidence.datasetcolumn_id].dataset
            id_to_dataset[dataset.id] = dataset
            rounded = float(x.value.quantize(Decimal('.1')))
            if rounded in expression_collapsed:
                expression_collapsed[rounded] += 1
            else:
                expression_collapsed[rounded] = 1

            sum += rounded;
            sum_of_squares += rounded*rounded;
            n += 1;

        if n == 0:
            overview = {'all_values': expression_collapsed,
                                               'high_values': [],
                                               'low_values': [],
                                               'low_cutoff': 0,
                                               'high_cutoff': 0}
        else:
            mean = 1.0*sum/n;
            variance = 1.0*sum_of_squares/n - mean*mean;
            standard_dev = variance**0.5;
            high_values = []
            low_values = []
            for x in expressionevidences:
                if float(x.value) >= mean + 4*standard_dev:
                    obj_json = x.to_json()
                    obj_json['datasetcolumn'] = x.evidence.datasetcolumn.to_min_json()
                    high_values.append(obj_json)
                elif float(x.value) <= mean - 4*standard_dev:
                    obj_json = x.to_json()
                    obj_json['datasetcolumn'] = x.evidence.datasetcolumn.to_min_json()
                    low_values.append(obj_json)
            overview = {'all_values': expression_collapsed,
                                               'high_values': high_values,
                                               'low_values': low_values,
                                               'low_cutoff': mean - 4*standard_dev,
                                               'high_cutoff': mean + 4*standard_dev}

        return json.dumps({'overview': overview,
                           'datasets': [x.to_semi_json() for x in id_to_dataset.values()]})

    else:
        evidences_json = []
        for x in expressionevidences:
            obj_json = x.to_json()
            obj_json['datasetcolumn'] = evidence.datasetcolumn.to_min_json()
            obj_json['dataset'] = evidence.datasetcolumn.dataset.to_min_json()
            obj_json['id'] = evidence.id
            evidences_json.append(obj_json)
        return json.dumps(evidences_json)

# -------------------------------Graph---------------------------------------
def create_node(bioent, is_focus, ev_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BIOENTITY' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'sub_type':sub_type, 'type': 'BIOENTITY'}}

def create_edge(bioent1_id, bioent2_id, score, class_type, direction):
    return {'data':{'target': 'BIOENTITY' + str(bioent1_id), 'source': 'BIOENTITY' + str(bioent2_id),
            'score':float(score), 'class_type': class_type, 'direction': direction}}

def make_graph(bioent_id):
    id_to_bioentity = dict([(x.id, x) for x in DBSession.query(Locus).all()])
    interactions = DBSession.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION').filter_by(bioentity_id=bioent_id).all()

    if len(interactions) == 0:
         return {'nodes': [], 'edges': []}
    neighbor_id_to_coeff = dict([(x.interactor_id, x.coeff) for x in interactions])

    max_coeff = 0

    coeff_to_interactions = dict()

    for interaction in interactions:
        coeff = interaction.coeff
        max_coeff = max_coeff if coeff <= max_coeff else coeff

        if coeff in coeff_to_interactions:
            coeff_to_interactions[coeff].append(interaction)
        else:
            coeff_to_interactions[coeff] = [interaction]

    #Apply 100 node cutoff
    all_neighbors = sorted(neighbor_id_to_coeff.keys(), key=lambda x: neighbor_id_to_coeff[x], reverse=True)
    usable_neighbor_ids = [x for x in all_neighbors][:100]
    usable_neighbor_ids.append(bioent_id)
    neighbor_id_to_coeff[bioent_id] = max_coeff
    min_coeff = 0 if len(usable_neighbor_ids) <= 100 else neighbor_id_to_coeff[all_neighbors[100]]

    more_interactions = DBSession.query(Bioentityinteraction).filter_by(interaction_type='EXPRESSION').filter(Bioentityinteraction.bioentity_id.in_(usable_neighbor_ids)).filter(Bioentityinteraction.interactor_id.in_(usable_neighbor_ids)).filter(Bioentityinteraction.bioentity_id < Bioentityinteraction.interactor_id).all()
    for interaction in more_interactions:
        coeff = interaction.coeff
        if coeff >= min_coeff:
            if coeff in coeff_to_interactions:
                coeff_to_interactions[coeff].append(interaction)
            else:
                coeff_to_interactions[coeff] = [interaction]

    all_coeffs = sorted(coeff_to_interactions.keys(), reverse=True)
    ok_interactions = set()
    cutoff_index = 0
    while len(ok_interactions) < 250 and cutoff_index < len(all_coeffs):
        cutoff = all_coeffs[cutoff_index]
        ok_nodes = set([x for x, y in neighbor_id_to_coeff.iteritems() if y >= cutoff])
        ok_interactions = set()
        for coeff, interactions in coeff_to_interactions.iteritems():
            if coeff >= cutoff:
                ok_interactions.update([x for x in interactions if x.bioentity_id in ok_nodes and x.interactor_id in ok_nodes])
        cutoff_index += 1

    cutoff_index -= 1
    min_coeff = max(min_coeff, all_coeffs[cutoff_index])

    usable_neighbor_ids = set([x for x in usable_neighbor_ids if neighbor_id_to_coeff[x] >= min_coeff])
    nodes = [create_node(id_to_bioentity[x], x==bioent_id, neighbor_id_to_coeff[x]) for x in usable_neighbor_ids]
    edges = [create_edge(x.bioentity_id, x.interactor_id, x.coeff, 'EXPRESSION', x.direction) for x in more_interactions if x.coeff >= min_coeff and x.bioentity_id in usable_neighbor_ids and x.interactor_id in usable_neighbor_ids]


    return {'nodes': nodes, 'edges': edges}
