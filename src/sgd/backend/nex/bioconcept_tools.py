from src.sgd.backend.nex import DBSession
from src.sgd.backend.nex.query_tools import get_relations, get_biofacts
from src.sgd.model.nex.bioconcept import Bioconceptrelation
from src.sgd.model.nex.bioconcept import Bioconcept
from src.sgd.model.nex.bioentity import Bioentity

__author__ = 'kpaskov'

# -------------------------------Ontology Graph---------------------------------------
def create_node(biocon, is_focus, sub_type):
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'Node' + str(biocon.id), 'name':biocon.display_name + ('' if biocon.count is None else ' (' + str(biocon.count.gene_count) + ')'), 'link': biocon.link, 'sub_type':sub_type}}

def create_edge(biocon1_id, biocon2_id, label):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id), 'name':label}}

def make_ontology_graph(bioconcept_id, class_type, filter_f, subtype_f):
    all_children = []
    bioconcept = DBSession.query(Bioconcept).filter_by(id=bioconcept_id).first()
    parent_relations = get_relations(Bioconceptrelation, class_type, child_ids=[bioconcept_id])
    child_relations = get_relations(Bioconceptrelation, class_type, parent_ids=[bioconcept_id])
    if len(parent_relations) > 0:
        grandparent_relations = get_relations(Bioconceptrelation, class_type, child_ids=[x.parent_id for x in parent_relations])
        greatgrandparent_relations = get_relations(Bioconceptrelation, class_type, child_ids=[x.parent_id for x in grandparent_relations])
        greatgreatgrandparent_relations = get_relations(Bioconceptrelation, class_type, child_ids=[x.parent_id for x in greatgrandparent_relations])

        nodes = [create_node(bioconcept, True, subtype_f(bioconcept))]

        parents = [x.parent for x in parent_relations]
        parents.extend([x.parent for x in grandparent_relations])
        parents.extend([x.parent for x in greatgrandparent_relations])
        parents.extend([x.parent for x in greatgreatgrandparent_relations])

        viable_ids = set([x.child_id for x in child_relations if filter_f(x.child)])

        #If there are too many children, hide some.
        hidden_children_count = 0
        if len(viable_ids) > 8:
            all_children = sorted(child_relations.child, key=lambda x: x.display_name)
            hidden_children_count = len(viable_ids)-7
            viable_ids = set(list(viable_ids)[:7])

        viable_ids.update([x.id for x in parents if filter_f(x)])
        viable_ids.add(bioconcept_id)

        nodes.extend([create_node(x.child, False, subtype_f(x)) for x in child_relations if x.child_id in viable_ids])
        nodes.extend([create_node(x, False, subtype_f(x)) for x in parents if x.id in viable_ids])

        relations = set()
        relations.update(parent_relations)
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
        nodes.extend([create_node(x.child, False, subtype_f(x)) for x in child_relations])
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in child_relations]

    return {'nodes': list(nodes), 'edges': edges, 'all_children': all_children}

# -------------------------------Graph-----------------------------------------
def create_bioent_node(bioent, is_focus, gene_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent.id), 'name':bioent.display_name, 'link': bioent.link,
                    'sub_type':sub_type, 'type': 'BIOENTITY', 'gene_count':gene_count}}

def create_biocon_node(bioconcept, sub_type, gene_count):
    return {'data':{'id':'BioconNode' + str(bioconcept.id), 'name':bioconcept.display_name, 'link': bioconcept.link, 'sub_type':sub_type, 'type': 'BIOCONCEPT', 'gene_count':gene_count}}

def create_bioent_biocon_edge(bioent_id, biocon_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'BioconNode' + str(biocon_id)}}

def make_graph(bioent_id, biocon_type, subtype_f, bioent_type='LOCUS'):

    #Get bioconcepts for gene
    bioconcept_ids = [x.bioconcept_id for x in get_biofacts(biocon_type, bioent_id=bioent_id)]

    biocon_id_to_bioent_ids = {}
    bioent_id_to_biocon_ids = {}

    if len(bioconcept_ids) > 0:
        all_relevant_biofacts = [x for x in get_biofacts(biocon_type, biocon_ids=bioconcept_ids, bioent_type=bioent_type)]
    else:
        all_relevant_biofacts = []

    for biofact in all_relevant_biofacts:
        bioentity_id = biofact.bioentity_id
        bioconcept_id = biofact.bioconcept_id

        if bioconcept_id in biocon_id_to_bioent_ids:
            biocon_id_to_bioent_ids[bioconcept_id].add(bioentity_id)
        else:
            biocon_id_to_bioent_ids[bioconcept_id] = {bioentity_id}

        if bioentity_id in bioent_id_to_biocon_ids:
            bioent_id_to_biocon_ids[bioentity_id].add(bioconcept_id)
        else:
            bioent_id_to_biocon_ids[bioentity_id] = {bioconcept_id}

    cutoff = 1
    node_count = len(bioent_id_to_biocon_ids) + len(biocon_id_to_bioent_ids)
    edge_count = len(all_relevant_biofacts)
    bioent_count = len(bioent_id_to_biocon_ids)
    bioent_ids_in_use = set([x for x, y in bioent_id_to_biocon_ids.iteritems() if len(y) >= cutoff])
    biocon_ids_in_use = set([x for x, y in biocon_id_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
    biofacts_in_use = [x for x in all_relevant_biofacts]
    while node_count > 100 or edge_count > 250 or bioent_count > 50:
        cutoff = cutoff + 1
        bioent_ids_in_use = set([x for x, y in bioent_id_to_biocon_ids.iteritems() if len(y) >= cutoff])
        biocon_ids_in_use = set([x for x, y in biocon_id_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
        biofacts_in_use = [x for x in all_relevant_biofacts if x.bioentity_id in bioent_ids_in_use and x.bioconcept_id in biocon_ids_in_use]
        node_count = len(bioent_ids_in_use) + len(biocon_ids_in_use)
        edge_count = len(biofacts_in_use)
        bioent_count = len(bioent_ids_in_use)

    if len(bioent_ids_in_use) > 0:

        bioent_to_score = dict({(x, len(y&biocon_ids_in_use)) for x, y in bioent_id_to_biocon_ids.iteritems()})
        bioent_to_score[bioent_id] = 0

        nodes = [create_bioent_node(x, x.id==bioent_id, bioent_to_score[x.id]) for x in DBSession.query(Bioentity).filter(Bioentity.id.in_(bioent_ids_in_use)).all()]
        nodes.extend([create_biocon_node(x, subtype_f(x), max(bioent_to_score[y] for y in biocon_id_to_bioent_ids[x.id])) for x in DBSession.query(Bioconcept).filter(Bioconcept.id.in_(biocon_ids_in_use)).all()])

        edges = [create_bioent_biocon_edge(biofact.bioentity_id, biofact.bioconcept_id) for biofact in biofacts_in_use]

        return {'nodes': nodes, 'edges': edges, 'max_cutoff': max(bioent_to_score.values()), 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x != bioent_id])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}