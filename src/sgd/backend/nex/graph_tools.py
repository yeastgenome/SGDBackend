from src.sgd.backend.nex import DBSession
from src.sgd.backend.nex.query_tools import get_relations, get_interactions_among
from src.sgd.model.nex.bioconcept import Bioconceptrelation
from src.sgd.model.nex.bioconcept import Bioconcept, Observable
from src.sgd.model.nex.bioentity import Locus
from src.sgd.model.nex.auxiliary import Interaction, Bioentityinteraction, Bioconceptinteraction, Bioiteminteraction, Referenceinteraction
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
    return {'data':{'id':'BIOENTITY' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'sub_type':sub_type, 'type': 'BIOENTITY', 'gene_count':gene_count}}

def create_interactor_node(bioconcept, gene_count):
    return {'data':{'id':'INTERACTOR' + str(bioconcept.id), 'name':bioconcept.display_name, 'link': bioconcept.link, 'gene_count':gene_count, 'type': 'INTERACTOR', 'sub_type': None}}

def create_interaction_edge(interaction):
    return {'data':{'target': 'BIOENTITY' + str(interaction.bioentity_id), 'source': 'INTERACTOR' + str(interaction.interactor_id)}}

def make_graph(bioent_id, interaction_cls, interaction_type, bioentity_type):
    interactions = DBSession.query(interaction_cls).filter_by(bioentity_id=bioent_id).filter_by(interaction_type=interaction_type).all()
    interactor_ids = set([x.interactor_id for x in interactions])

    interactor_ids_to_bioent_ids = {}
    bioent_ids_to_interactor_ids = {}

    all_relevant_interactions = []
    if len(interactor_ids) > 0:
        all_relevant_interactions = DBSession.query(interaction_cls).filter_by(interaction_type=interaction_type).filter(interaction_cls.interactor_id.in_(interactor_ids)).all()

    for interaction in all_relevant_interactions:
        bioentity_id = interaction.bioentity_id
        interactor_id = interaction.interactor_id

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
    bioent_ids_in_use = set([x for x, y in bioent_ids_to_interactor_ids.iteritems() if len(y) >= cutoff])
    interactor_ids_in_use = set([x for x, y in interactor_ids_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
    interactions_in_use = [x for x in all_relevant_interactions]

    while node_count > 100 or edge_count > 250 or bioent_count > 50:
        cutoff = cutoff + 1
        bioent_ids_in_use = set([x for x, y in bioent_ids_to_interactor_ids.iteritems() if len(y) >= cutoff])
        interactor_ids_in_use = set([x for x, y in interactor_ids_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
        interactions_in_use = [x for x in all_relevant_interactions if x.bioentity_id in bioent_ids_in_use and x.interactor_id in interactor_ids_in_use]
        node_count = len(bioent_ids_in_use) + len(interactor_ids_in_use)
        edge_count = len(interactions_in_use)
        bioent_count = len(bioent_ids_in_use)

    if len(bioent_ids_in_use) > 0:
        edges = [create_interaction_edge(interaction) for interaction in interactions_in_use]

        bioent_to_score = dict({(x, len(y&interactor_ids_in_use)) for x, y in bioent_ids_to_interactor_ids.iteritems()})
        bioent_to_score[bioent_id] = 0

        id_to_nodes = dict([(x.bioentity_id, create_bioent_node(x.bioentity, x.bioentity_id==bioent_id, bioent_to_score[x.bioentity_id])) for x in interactions_in_use])
        id_to_nodes.update([(x.interactor_id, create_interactor_node(x.interactor, max(bioent_to_score[y] for y in interactor_ids_to_bioent_ids[x.interactor_id]))) for x in interactions_in_use])

        max_cutoff = max(bioent_to_score.values())
        id_to_nodes[bioent_id]['data']['gene_count'] = max_cutoff

        return {'nodes': id_to_nodes.values(), 'edges': edges, 'max_cutoff': max_cutoff, 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x != bioent_id])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}

# -------------------------------Interaction Graph---------------------------------------
def create_interaction_graph_node(x):
    return {'data':{'id':'BIOENTITY' + str(x.id), 'name':x.display_name, 'link': x.link}}

def create_interaction_graph_edge(x):
    return {'data':{'target': 'BIOENTITY' + str(x.bioentity_id), 'source': 'BIOENTITY' + str(x.interactor_id)}}

def make_interaction_graph(locus_ids, interaction_cls, interaction_type):
    edges = [create_interaction_graph_edge(x) for x in get_interactions_among(locus_ids, interaction_cls, interaction_type)]
    nodes = [create_interaction_graph_node(x) for x in DBSession.query(Locus).filter(Locus.id.in_(locus_ids))]

    return {'nodes': list(nodes), 'edges': edges}

def get_interactions_among(locus_ids, interaction_cls, interaction_type):
    interactions = DBSession.query(interaction_cls).filter_by(interaction_type=interaction_type).filter(interaction_cls.bioentity_id.in_(locus_ids)).filter(interaction_cls.interactor_id.in_(locus_ids)).all()

    pair_to_edge = {}
    for interaction in interactions:
        pair = (interaction.bioentity_id, interaction.interactor_id)
        if interaction.direction == 'undirected' and interaction.bioentity_id < interaction.interactor_id:
            pair = (interaction.interactor_id, interaction.bioentity_id)
        if interaction.direction == 'backward':
            pair = (interaction.bioentity_id, interaction.interactor_id)
        pair_to_edge[pair] = interaction
    return pair_to_edge.values()