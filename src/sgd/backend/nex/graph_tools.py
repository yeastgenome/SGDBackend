from src.sgd.backend.nex import DBSession
from src.sgd.backend.nex.query_tools import get_relations, get_interactions_among
from src.sgd.model.nex.bioconcept import Bioconceptrelation
from src.sgd.model.nex.bioconcept import Bioconcept, Observable, Phenotype
from src.sgd.model.nex.bioitem import Bioitem
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
        name = name + ' (' + str(biocon.locus_count) + ')'
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
        all_children = sorted([x.child for x in child_relations], key=lambda x: x.display_name.lower())
        if len(viable_ids) > 8:
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
            grandchild_relations = [x for x in get_relations(Bioconceptrelation, None, parent_ids=[x.child_id for x in child_relations]) if x.relation_type == 'is a']
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

    if len(locus_ids) > 0:
        query = DBSession.query(interaction_cls).filter_by(interaction_type=interaction_type).filter(interaction_cls.bioentity_id.in_(locus_ids)).filter(interaction_cls.interactor_id.in_(locus_ids))
        if min_evidence_count > 0:
            query = query.filter(interaction_cls.evidence_count >= min_evidence_count)
        interactions = query.all()
    else:
        interactions = []

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
def create_lsp_node(bioent, is_focus):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BIOENTITY' + str(bioent.id),
                    'name':bioent.display_name,
                    'link': bioent.link,
                    'sub_type':sub_type,
                    'type': 'BIOENTITY'}}

def create_lsp_edge(bioent1_id, bioent2_id, interaction_type, count):
    return {'data':{'target': 'BIOENTITY' + str(bioent1_id), 'source': 'BIOENTITY' + str(bioent2_id), 'type': interaction_type, 'count': count}}

def make_lsp_graph(locus_id, node_max=100, edge_max=250):

    #Get interactors
    bioconcept_ids = [(x.interaction_type, x.interactor_id) for x in DBSession.query(Bioconceptinteraction).filter_by(bioentity_id=locus_id).all()]
    bioitem_ids = [(x.interaction_type, x.interactor_id) for x in DBSession.query(Bioiteminteraction).filter_by(bioentity_id=locus_id).all()]

    print len(bioconcept_ids) + len(bioitem_ids)

    interactor_to_bioent_ids = dict()
    bioent_id_to_interactor_ids = dict()

    #Get next level
    num_chunks = int(ceil(1.0*len(bioconcept_ids)/500))
    for i in range(0, num_chunks):
        for interaction in DBSession.query(Bioconceptinteraction).filter(Bioconceptinteraction.interactor_id.in_([x[1] for x in bioconcept_ids[i*500:(i+1)*500]])).all():
            key = (interaction.interaction_type, interaction.interactor_id)
            bioentity_id = interaction.bioentity_id
            if key in interactor_to_bioent_ids:
                interactor_to_bioent_ids[key].add(bioentity_id)
            else:
                interactor_to_bioent_ids[key] = set([bioentity_id])
            if bioentity_id in bioent_id_to_interactor_ids:
                bioent_id_to_interactor_ids[bioentity_id].add(key)
            else:
                bioent_id_to_interactor_ids[bioentity_id] = set([key])

    num_chunks = int(ceil(1.0*len(bioitem_ids)/500))
    for i in range(0, num_chunks):
        for interaction in DBSession.query(Bioiteminteraction).filter(Bioiteminteraction.interactor_id.in_([x[1] for x in bioitem_ids[i*500:(i+1)*500]])).all():
            key = (interaction.interaction_type, interaction.interactor_id)
            bioentity_id = interaction.bioentity_id
            if key in interactor_to_bioent_ids:
                interactor_to_bioent_ids[key].add(bioentity_id)
            else:
                interactor_to_bioent_ids[key] = set([bioentity_id])
            if bioentity_id in bioent_id_to_interactor_ids:
                bioent_id_to_interactor_ids[bioentity_id].add(key)
            else:
                bioent_id_to_interactor_ids[bioentity_id] = set([key])

    bioent_ids_in_use = set()
    min_cutoff = max(len(y) for y in bioent_id_to_interactor_ids.values())
    while len(bioent_ids_in_use) + len([x for x, y in bioent_id_to_interactor_ids.iteritems() if len(y) == min_cutoff]) < node_max:
        bioent_ids_in_use.update([x for x, y in bioent_id_to_interactor_ids.iteritems() if len(y) == min_cutoff])
        min_cutoff -= 1

    #Pick out cutoff
    pair_to_score = dict()
    for bioent1_id in bioent_ids_in_use:
        for bioent2_id in bioent_ids_in_use:
            if bioent1_id < bioent2_id:
                overlap = bioent_id_to_interactor_ids[bioent1_id] & bioent_id_to_interactor_ids[bioent2_id]
                domain_count = len([x for x in overlap if x[0] == 'DOMAIN'])
                phenotype_count = len([x for x in overlap if x[0] == 'PHENOTYPE'])
                go_count = len([x for x in overlap if x[0] == 'GO'])
                score = int(ceil(.5*domain_count + .5*phenotype_count + go_count))
                pair_to_score[(bioent1_id, bioent2_id)] = score

    interactions = DBSession.query(Bioentityinteraction).filter(Bioentityinteraction.bioentity_id.in_(bioent_ids_in_use)).filter(Bioentityinteraction.evidence_count > 2).all()
    pair_to_interactions = dict()
    for interaction in interactions:
        if interaction.bioentity_id < interaction.interactor_id:
            key = (interaction.bioentity_id, interaction.interactor_id)
            if interaction.interaction_type == 'EXPRESSION':
                score = max(0, (interaction.coeff - .75)*20)
            else:
                score = interaction.evidence_count-2
        elif interaction.bioentity_id > interaction.interactor_id:
            key = (interaction.interactor_id, interaction.bioentity_id)
            if interaction.interaction_type == 'EXPRESSION':
                score = max(0, (interaction.coeff - .75)*20)
            else:
                score = interaction.evidence_count-2
        else:
            key = (interaction.bioentity_id, interaction.interactor_id)
            if interaction.interaction_type == 'EXPRESSION':
                score = max(0, (interaction.coeff - .75)*10)
            else:
                score = 1.0*(interaction.evidence_count-2)/2
        if key in pair_to_score:
            pair_to_score[key] += score
        else:
            pair_to_score[key] = score
        if key in pair_to_interactions:
            pair_to_interactions[key].append(interaction)
        else:
            pair_to_interactions[key] = [interaction]

    min_edge_cutoff = max(pair_to_score.values())
    score_to_bioent_ids = dict([(i, set()) for i in range(0, min_edge_cutoff+1)])
    for bioent_id in bioent_ids_in_use:
        if bioent_id < locus_id:
            score = pair_to_score[(bioent_id, locus_id)]
        elif bioent_id > locus_id:
            score = pair_to_score[(locus_id, bioent_id)]
        else:
            score = min_edge_cutoff+1
        for i in range(0, score):
            score_to_bioent_ids[i].add(bioent_id)

    pairs_in_use = set()

    while len([x for x,y in pair_to_score.iteritems() if y>=min_edge_cutoff and x[0] in score_to_bioent_ids[min_edge_cutoff] and x[1] in score_to_bioent_ids[min_edge_cutoff]]) < edge_max and min_edge_cutoff > 0:
        pairs_in_use.update([x for x,y in pair_to_score.iteritems() if y>=min_edge_cutoff and x[0] in score_to_bioent_ids[min_edge_cutoff] and x[1] in score_to_bioent_ids[min_edge_cutoff]])
        min_edge_cutoff -= 1

    new_bioent_ids_in_use = score_to_bioent_ids[min_edge_cutoff+1]

    id_to_nodes = {}
    id_to_nodes.update([(x.id, create_lsp_node(x, x.id==locus_id)) for x in DBSession.query(Locus).filter(Locus.id.in_(new_bioent_ids_in_use)).all()])

    edges = []
    for bioent1_id, bioent2_id in pairs_in_use:
        interaction_types = [x[0] for x in bioent_id_to_interactor_ids[bioent1_id] & bioent_id_to_interactor_ids[bioent2_id]]
        interaction_type_to_count = {}
        for interaction_type in interaction_types:
            if interaction_type in interaction_type_to_count:
                interaction_type_to_count[interaction_type] += 1
            else:
                interaction_type_to_count[interaction_type] = 1
        if (bioent1_id, bioent2_id) in pair_to_interactions:
            for interaction in pair_to_interactions[(bioent1_id, bioent2_id)]:
                interaction_type_to_count[interaction.interaction_type] = interaction.evidence_count-2

        for interaction_type, count in interaction_type_to_count.iteritems():
            if bioent1_id != bioent2_id:
                edges.append(create_lsp_edge(bioent1_id, bioent2_id, interaction_type, min(count, 5)))

    #Pick out interactors to highlight
    interactor_ids_in_use = set()
    for bioent_id in new_bioent_ids_in_use:
        interactor_ids_in_use.update(bioent_id_to_interactor_ids[bioent_id])

    interactor_id_to_score = dict()
    for interactor_id, bioent_ids in interactor_to_bioent_ids.iteritems():
        overlap = len(bioent_ids & new_bioent_ids_in_use)
        if overlap > 1:
            score = 1.0*overlap/len(bioent_ids)
        else:
            score = 0
        interactor_id_to_score[interactor_id] = score

    top_interactors = [x for x in sorted(interactor_ids_in_use, key=lambda x: interactor_id_to_score[x], reverse=True)][:20]

    top_bioitems = []
    top_bioconcepts = []
    for interactor_id in top_interactors:
        if interactor_id_to_score[interactor_id] > 0:
            if interactor_id in bioconcept_ids:
                top_bioconcepts.append(interactor_id)
            elif interactor_id in bioitem_ids:
                top_bioitems.append(interactor_id)

    top_bioconcept_info = []
    top_bioitem_info = []
    if len(top_bioconcepts) > 0:
        top_bioconcept_info.extend([get_class_too(x) for x in DBSession.query(Bioconcept).filter(Bioconcept.id.in_([x[1] for x in top_bioconcepts])).all()])
    if len(top_bioitems) > 0:
        top_bioitem_info.extend([get_class_too(x) for x in DBSession.query(Bioitem).filter(Bioitem.id.in_([x[1] for x in top_bioitems])).all()])

    for interactor_id in top_bioconcepts:
        for bioent_id in interactor_to_bioent_ids[interactor_id]:
            if bioent_id in id_to_nodes:
                id_to_nodes[bioent_id]['data']['BIOCONCEPT' + str(interactor_id[1])] = True
    for interactor_id in top_bioitems:
        for bioent_id in interactor_to_bioent_ids[interactor_id]:
            if bioent_id in id_to_nodes:
                id_to_nodes[bioent_id]['data']['BIOITEM' + str(interactor_id[1])] = True

    return {'nodes': id_to_nodes.values(), 'edges': edges, 'top_bioconcepts': top_bioconcept_info, 'top_bioitems': top_bioitem_info}

def get_class_too(x):
    obj_json = x.to_min_json()
    obj_json['class_type'] = x.class_type
    return obj_json