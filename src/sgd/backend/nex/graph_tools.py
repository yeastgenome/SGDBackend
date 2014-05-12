from src.sgd.backend.nex import DBSession
from src.sgd.backend.nex.query_tools import get_relations, get_interactions_among
from src.sgd.model.nex.bioconcept import Bioconceptrelation
from src.sgd.model.nex.bioconcept import Bioconcept, Observable
from src.sgd.model.nex.bioentity import Locus
from src.sgd.model.nex.auxiliary import Interaction, Bioentityinteraction, Bioconceptinteraction, Bioiteminteraction, Referenceinteraction
from sqlalchemy.orm import joinedload
from math import ceil

__author__ = 'kpaskov'

# -------------------------------Ontology Graph---------------------------------------
def create_node(biocon, is_focus, sub_type):
    if is_focus:
        sub_type = 'FOCUS'
    name = biocon.display_name
    if biocon.format_name != 'ypo':
        name = name + ' (' + str(biocon.count) + ')'
    return {'data':{'id':'Node' + str(biocon.id), 'name': name, 'link': biocon.link, 'sub_type':sub_type}}

def create_edge(biocon1_id, biocon2_id, label):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id), 'name':label}}

def make_ontology_graph(bioconcept_id, class_type, filter_f, subtype_f):
    full_ontology = None
    all_children = []
    bioconcept = DBSession.query(Bioconcept).filter_by(id=bioconcept_id).first()
    parent_relations = [x for x in get_relations(Bioconceptrelation, None, child_ids=[bioconcept_id]) if x.relation_type != 'GO_SLIM']
    child_relations = [x for x in get_relations(Bioconceptrelation, None, parent_ids=[bioconcept_id]) if x.relation_type != 'GO_SLIM']
    if len(parent_relations) > 0:
        grandparent_relations = [x for x in get_relations(Bioconceptrelation, None, child_ids=[x.parent_id for x in parent_relations]) if x.relation_type != 'GO_SLIM']
        greatgrandparent_relations = [x for x in get_relations(Bioconceptrelation, None, child_ids=[x.parent_id for x in grandparent_relations]) if x.relation_type != 'GO_SLIM']
        greatgreatgrandparent_relations = [x for x in get_relations(Bioconceptrelation, None, child_ids=[x.parent_id for x in greatgrandparent_relations]) if x.relation_type != 'GO_SLIM']

        nodes = [create_node(bioconcept, True, subtype_f(bioconcept))]

        parents = [x.parent for x in parent_relations]
        parents.extend([x.parent for x in grandparent_relations])
        parents.extend([x.parent for x in greatgrandparent_relations])
        parents.extend([x.parent for x in greatgreatgrandparent_relations])

        viable_ids = set([x.child_id for x in child_relations if filter_f(x.child)])

        #If there are too many children, hide some.
        hidden_children_count = 0
        if len(viable_ids) > 8:
            all_children = sorted([x.child for x in child_relations], key=lambda x: x.display_name)
            hidden_children_count = len(viable_ids)-7
            viable_ids = set(list(viable_ids)[:7])

        viable_ids.update([x.id for x in parents if filter_f(x)])
        viable_ids.add(bioconcept_id)

        nodes.extend([create_node(x.child, False, subtype_f(x.child)) for x in child_relations if x.child_id in viable_ids])
        nodes.extend([create_node(x, False, subtype_f(x)) for x in parents if x.id in viable_ids])

        relations = set()
        relations.update(child_relations)
        relations.update(parent_relations)
        relations.update(grandparent_relations)
        relations.update(greatgrandparent_relations)
        relations.update(greatgreatgrandparent_relations)
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in relations if x.child_id in viable_ids and x.parent_id in viable_ids]

        if hidden_children_count > 0:
            nodes.insert(0, {'data':{'id':'NodeMoreChildren', 'name':str(hidden_children_count) + ' more children', 'link': None, 'sub_type':subtype_f(bioconcept)}})
            edges.insert(0, {'data':{'target': 'NodeMoreChildren', 'source': 'Node' + str(bioconcept_id), 'name':None}})

    else:
        nodes = [create_node(bioconcept, True, subtype_f(bioconcept))]
        nodes.extend([create_node(x.child, False, subtype_f(x.child)) for x in child_relations])
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in child_relations]

        if bioconcept.class_type == 'OBSERVABLE':
            grandchild_relations = [x for x in get_relations(Bioconceptrelation, None, parent_ids=[x.child_id for x in child_relations])]
            nodes.extend([create_node(x.child, False, subtype_f(x.child)) for x in grandchild_relations])
            edges.extend([create_edge(x.child_id, x.parent_id, x.relation_type) for x in grandchild_relations])

            observables = DBSession.query(Observable).all()
            elements = [x.to_min_json() for x in sorted(observables, key=lambda x: x.display_name)]
            child_to_parent = dict([(x.child_id, x.parent_id) for y in observables for x in y.children])
            full_ontology = {'elements': elements, 'child_to_parent': child_to_parent}

    obj_json = {'nodes': list(nodes), 'edges': edges, 'all_children': [x.to_min_json() for x in all_children]}
    if full_ontology is not None:
        obj_json['full_ontology'] = full_ontology
    return obj_json

# -------------------------------Graph-----------------------------------------
def create_bioent_node(bioent, is_focus, gene_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BIOENTITY' + str(bioent.id),
                    'name':bioent.display_name,
                    'link': bioent.link,
                    'sub_type':sub_type,
                    'type': 'BIOENTITY',
                    'gene_count':gene_count,
                    'source': bioent.source.display_name}}

def create_interactor_node(bioconcept, gene_count):
    return {'data':{'id':'INTERACTOR_' + bioconcept.class_type + str(bioconcept.id),
                    'name':bioconcept.display_name,
                    'link': bioconcept.link,
                    'gene_count':gene_count,
                    'type': bioconcept.class_type,
                    'sub_type': None,
                    'source': bioconcept.source.display_name}}

def create_interaction_edge(interaction, interaction_type):
    if interaction_type == 'PHENOTYPE':
        source = 'INTERACTOR_OBSERVABLE' + str(interaction.interactor_id)
    else:
        source = 'INTERACTOR_' + interaction_type + str(interaction.interactor_id)
    return {'data':{'target': 'BIOENTITY' + str(interaction.bioentity_id), 'source': source}}

def make_graph(bioent_id, interaction_cls, interaction_type, bioentity_type, node_max=100, edge_max=250, bioent_max=50, interactor_max=100):
    interactions = DBSession.query(interaction_cls).filter_by(bioentity_id=bioent_id).filter_by(interaction_type=interaction_type).all()
    interactor_ids = set([x.interactor_id for x in interactions])

    id_to_bioentity = {}
    id_to_interactor = {}
    interactor_ids_to_bioent_ids = {}
    bioent_ids_to_interactor_ids = {}

    all_relevant_interactions = []
    if len(interactor_ids) > 0:
        all_relevant_interactions = DBSession.query(interaction_cls).filter_by(interaction_type=interaction_type).filter(interaction_cls.interactor_id.in_(interactor_ids)).options(joinedload('bioentity'), joinedload('interactor')).all()

    for interaction in all_relevant_interactions:
        bioentity_id = interaction.bioentity_id
        interactor_id = interaction.interactor_id
        id_to_bioentity[bioentity_id] = interaction.bioentity
        id_to_interactor[interactor_id] = interaction.interactor

        if interaction.bioentity.class_type == bioentity_type:
            if interactor_id in interactor_ids_to_bioent_ids:
                interactor_ids_to_bioent_ids[interactor_id].add(bioentity_id)
            else:
                interactor_ids_to_bioent_ids[interactor_id] = {bioentity_id}

            if bioentity_id in bioent_ids_to_interactor_ids:
                bioent_ids_to_interactor_ids[bioentity_id].add(interactor_id)
            else:
                bioent_ids_to_interactor_ids[bioentity_id] = {interactor_id}

    cutoff = 1
    node_count = len(bioent_ids_to_interactor_ids) + len(interactor_ids_to_bioent_ids)
    edge_count = len(all_relevant_interactions)
    bioent_count = len(bioent_ids_to_interactor_ids)
    interactor_count = len(interactor_ids_to_bioent_ids)
    bioent_ids_in_use = set([x for x, y in bioent_ids_to_interactor_ids.iteritems() if len(y) >= cutoff])
    interactor_ids_in_use = set([x for x, y in interactor_ids_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
    interactions_in_use = [x for x in all_relevant_interactions]

    while node_count > node_max or edge_count > edge_max or bioent_count > bioent_max or interactor_count > interactor_max:
        cutoff = cutoff + 1
        bioent_ids_in_use = set([x for x, y in bioent_ids_to_interactor_ids.iteritems() if len(y) >= cutoff])
        interactor_ids_in_use = set([x for x, y in interactor_ids_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
        interactions_in_use = [x for x in all_relevant_interactions if x.bioentity_id in bioent_ids_in_use and x.interactor_id in interactor_ids_in_use]
        node_count = len(bioent_ids_in_use) + len(interactor_ids_in_use)
        edge_count = len(interactions_in_use)
        bioent_count = len(bioent_ids_in_use)
        interactor_count = len(interactor_ids_in_use)

    if bioent_count > 0 and interactor_count > 0:
        edges = [create_interaction_edge(interaction, interaction_type) for interaction in interactions_in_use]

        bioent_to_score = dict({(x, len(bioent_ids_to_interactor_ids[x]&interactor_ids_in_use)) for x in bioent_ids_in_use})
        bioent_to_score[bioent_id] = 0

        id_to_nodes = dict([(x, create_bioent_node(id_to_bioentity[x], x==bioent_id, bioent_to_score[x])) for x in bioent_ids_in_use])
        id_to_nodes.update([(x, create_interactor_node(id_to_interactor[x], max(bioent_to_score[y] for y in interactor_ids_to_bioent_ids[x]&bioent_ids_in_use))) for x in interactor_ids_in_use])

        max_cutoff = max(bioent_to_score.values())
        id_to_nodes[bioent_id]['data']['gene_count'] = max_cutoff

        return {'nodes': id_to_nodes.values(), 'edges': edges, 'max_cutoff': max_cutoff, 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x != bioent_id])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}

# -------------------------------Interaction Graph---------------------------------------
def create_interaction_graph_node(x):
    return {'data':{'id':'BIOENTITY' + str(x.id), 'name':x.display_name, 'link': x.link, 'type': 'BIOENTITY', 'sub_type': None}}

def create_interaction_graph_edge(x):
    return {'data':{'target': 'BIOENTITY' + str(x.bioentity_id), 'source': 'BIOENTITY' + str(x.interactor_id)}}

def make_interaction_graph(locus_ids, interaction_cls, interaction_type, min_evidence_count=0):
    edges = [create_interaction_graph_edge(x) for x in get_interactions_among(locus_ids, interaction_cls, interaction_type, min_evidence_count)]
    nodes = [create_interaction_graph_node(x) for x in DBSession.query(Locus).filter(Locus.id.in_(locus_ids))]

    return {'nodes': list(nodes), 'edges': edges}

def get_interactions_among(locus_ids, interaction_cls, interaction_type, min_evidence_count=0):

    query = DBSession.query(interaction_cls).filter_by(interaction_type=interaction_type).filter(interaction_cls.bioentity_id.in_(locus_ids)).filter(interaction_cls.interactor_id.in_(locus_ids))
    if min_evidence_count > 0:
        query = query.filter(interaction_cls.evidence_count >= min_evidence_count)
    interactions = query.all()

    pair_to_edge = {}
    for interaction in interactions:
        pair = (interaction.bioentity_id, interaction.interactor_id)
        if interaction.direction == 'undirected' and interaction.bioentity_id < interaction.interactor_id:
            pair = (interaction.interactor_id, interaction.bioentity_id)
        if interaction.direction == 'backward':
            pair = (interaction.bioentity_id, interaction.interactor_id)
        pair_to_edge[pair] = interaction
    return pair_to_edge.values()

# -------------------------------LSP Graph---------------------------------------
def make_lsp_graph(locus_id, node_max=100, edge_max=250):

    interactor_id_to_count = {}

    all_relevant_interactions = []

    bioconcept_interactor_ids = set([x.interactor_id for x in DBSession.query(Bioconceptinteraction).filter_by(bioentity_id=locus_id).all()])
    if len(bioconcept_interactor_ids) > 0:
        all_relevant_interactions.extend(DBSession.query(Bioconceptinteraction).filter(Bioconceptinteraction.interactor_id.in_(bioconcept_interactor_ids)).options(joinedload('interactor')).all())
    bioitem_interactor_ids = set([x.interactor_id for x in DBSession.query(Bioiteminteraction).filter_by(bioentity_id=locus_id).all()])
    if len(bioitem_interactor_ids) > 0:
        all_relevant_interactions.extend(DBSession.query(Bioiteminteraction).filter(Bioiteminteraction.interactor_id.in_(bioitem_interactor_ids)).options(joinedload('interactor')).all())

    relation_to_score = {}
    id_to_bioentity = {}
    for interaction in all_relevant_interactions:
        bioentity_id = interaction.bioentity_id

        id_to_bioentity[bioentity_id] = interaction.bioentity
        if bioentity_id != locus_id:
            key = (min(locus_id, bioentity_id), max(locus_id, bioentity_id), interaction.interaction_type)
            if interaction.interaction_type + str(interaction.interactor_id) not in interactor_id_to_count:
                interactor_id_to_count[interaction.interaction_type + str(interaction.interactor_id)] = interaction.interactor.count
            count = interactor_id_to_count[interaction.interaction_type + str(interaction.interactor_id)]
            if key in relation_to_score:
                relation_to_score[key] += 100.0/count
            else:
                relation_to_score[key] = 100.0/count

    for interaction in DBSession.query(Bioentityinteraction).filter_by(bioentity_id=locus_id).options(joinedload('interactor')).all():
        id_to_bioentity[interaction.interactor_id] = interaction.interactor
        key = (min(locus_id, interaction.interactor_id), max(locus_id, interaction.interactor_id), interaction.interaction_type)
        relation_to_score[key] = interaction.evidence_count

    bioent_id_to_score = dict([(x, 0) for x in id_to_bioentity.keys()])
    max_score = 1
    for relation_tuple, score in relation_to_score.iteritems():
        bioentity_id, interactor_id, interaction_type = relation_tuple
        other_id = bioentity_id if bioentity_id != locus_id else interactor_id
        if score > interaction_type_to_score[interaction_type]:
            if other_id in bioent_id_to_score:
                bioent_id_to_score[other_id] += 1
                if bioent_id_to_score[other_id] > max_score:
                    max_score = bioent_id_to_score[other_id]
            else:
                bioent_id_to_score[other_id] = 1

    bioent_ids_in_use = []
    min_score = max_score
    while len(bioent_ids_in_use) + len([x for x, y in bioent_id_to_score.iteritems() if y >= min_score]) < node_max:
        bioent_ids_in_use.extend([x for x, y in bioent_id_to_score.iteritems() if y == min_score])
        min_score -= 1

    if locus_id in bioent_ids_in_use:
        bioent_ids_in_use.remove(locus_id)

    #Bioconcepts
    bioconcept_to_bioent_ids = {}
    for interaction in DBSession.query(Bioconceptinteraction).filter(Bioconceptinteraction.bioentity_id.in_(bioent_ids_in_use)).options(joinedload('interactor')).all():
        if (interaction.interactor_id, interaction.interaction_type) in bioconcept_to_bioent_ids:
            bioconcept_to_bioent_ids[(interaction.interactor_id, interaction.interaction_type)].add(interaction.bioentity_id)
        else:
            bioconcept_to_bioent_ids[(interaction.interactor_id, interaction.interaction_type)] = set([interaction.bioentity_id])
        if interaction.interaction_type + str(interaction.interactor_id) not in interactor_id_to_count:
            interactor_id_to_count[interaction.interaction_type + str(interaction.interactor_id)] = interaction.interactor.count

    for bioconcept_tuple, bioent_ids in bioconcept_to_bioent_ids.iteritems():
        bioconcept_id, interaction_type = bioconcept_tuple
        count = interactor_id_to_count[interaction_type + str(bioconcept_id)]
        for bioent_id1 in bioent_ids:
            for bioent_id2 in bioent_ids:
                if bioent_id1 < bioent_id2:
                    key = (min(bioent_id1, bioent_id2), max(bioent_id1, bioent_id2), interaction_type)
                    if key in relation_to_score:
                        relation_to_score[key] += 100.0/count
                    else:
                        relation_to_score[key] = 100.0/count

    #Bioitems
    bioitem_to_bioent_ids = {}
    for interaction in DBSession.query(Bioiteminteraction).filter(Bioiteminteraction.bioentity_id.in_(bioent_ids_in_use)).options(joinedload('interactor')).all():
        if (interaction.interactor_id, interaction.interaction_type) in bioitem_to_bioent_ids:
            bioitem_to_bioent_ids[(interaction.interactor_id, interaction.interaction_type)].add(interaction.bioentity_id)
        else:
            bioitem_to_bioent_ids[(interaction.interactor_id, interaction.interaction_type)] = set([interaction.bioentity_id])
        if interaction.interaction_type + str(interaction.interactor_id) not in interactor_id_to_count:
            interactor_id_to_count[interaction.interaction_type + str(interaction.interactor_id)] = interaction.interactor.count

    for bioitem_tuple, bioent_ids in bioitem_to_bioent_ids.iteritems():
        bioitem_id, interaction_type = bioitem_tuple
        count = interactor_id_to_count[interaction_type + str(bioitem_id)]
        for bioent_id1 in bioent_ids:
            for bioent_id2 in bioent_ids:
                if bioent_id1 < bioent_id2:
                    key = (min(bioent_id1, bioent_id2), max(bioent_id1, bioent_id2), interaction_type)
                    if key in relation_to_score:
                        relation_to_score[key] += 100.0/count
                    else:
                        relation_to_score[key] = 100.0/count

    #Bioentities
    for interaction in DBSession.query(Bioentityinteraction).filter(Bioentityinteraction.bioentity_id.in_(bioent_ids_in_use)).filter(Bioentityinteraction.interactor_id.in_(bioent_ids_in_use)).all():
        key = (min(interaction.bioentity_id, interaction.interactor_id), max(interaction.bioentity_id, interaction.interactor_id), interaction.interaction_type)
        relation_to_score[key] = interaction.evidence_count

    bioent_ids_in_use.append(locus_id)
    print len(bioent_ids_in_use)

    nodes = [create_bioent_node(id_to_bioentity[x], x==locus_id, max_score if x==locus_id else bioent_id_to_score[x]) for x in bioent_ids_in_use]
    edges = []
    for relation_tuple, score in relation_to_score.iteritems():
        bioentity_id, interactor_id, interaction_type = relation_tuple
        if score >= interaction_type_to_score[interaction_type] and bioentity_id in bioent_ids_in_use and interactor_id in bioent_ids_in_use:
            edges.append({'data':{'target': 'BIOENTITY' + str(bioentity_id), 'source': 'BIOENTITY' + str(interactor_id), 'type': interaction_type}})

    return {'nodes': nodes, 'edges': edges, 'max_cutoff': max_score, 'min_cutoff':min_score}

interaction_type_to_score = {'DOMAIN': 3, 'PHENOTYPE': 3, 'GO': 3, 'PHYSINTERACTION': 3, 'GENINTERACTION': 3, 'REGULATION': 1000}