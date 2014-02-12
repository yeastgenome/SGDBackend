from model_new_schema import create_format_name
from model_new_schema.bioconcept import Complex
from sgdbackend import view_go
from sgdbackend_query.query_auxiliary import get_biofacts, get_interactions_among

__author__ = 'kpaskov'

from sgdbackend_utils.cache import id_to_biocon, id_to_bioent


# -------------------------------Genes-----------------------------------------
def make_genes(complex_id):
    from sgdbackend_utils.cache import id_to_biocon, id_to_bioent
    return [id_to_bioent[x.bioentity_id] for x in get_biofacts('GO', biocon_id=id_to_biocon[complex_id]['go']['id'])]

'''
-------------------------------Details---------------------------------------
'''
def make_details(complex_id):
    return view_go.make_details(go_id=id_to_biocon[complex_id]['go']['id'])

# -------------------------------Graph-----------------------------------------

def create_complex_node(bioent, is_focus, gene_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'],
                    'sub_type':sub_type, 'type': 'BIOENTITY', 'gene_count':gene_count}}

def create_biocon_node(biocon, gene_count):
    return {'data':{'id':'BioconNode' + str(biocon['id']), 'name':biocon['display_name'], 'link': biocon['link'],
                    'sub_type':None, 'type': 'BIOCONCEPT', 'gene_count':gene_count}}

def create_edge(bioent_id, biocon_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'BioconNode' + str(biocon_id)}}

def make_graph(complex_id):

    #Get genes for complex
    bioentity_ids = [x['id'] for x in make_genes(complex_id)]

    #Get bioconcepts for complex
    bioconcept_ids = [x.bioconcept_id for x in get_biofacts('GO', bioent_ids=bioentity_ids) if id_to_biocon[x.bioconcept_id]['go_aspect'] == 'biological process']

    if len(bioconcept_ids) > 0:
        all_relevant_biofacts = [x for x in get_biofacts('GO', biocon_ids=bioconcept_ids)]
    else:
        all_relevant_biofacts = []

    go_id_to_complex_id = dict([(x['go']['id'], x['id']) for x in id_to_biocon.values() if x['class_type'] == 'COMPLEX'])
    bioent_id_to_complex_ids = {}
    for biofact in get_biofacts('GO', biocon_ids=go_id_to_complex_id.keys()):
        if biofact.bioentity_id in bioent_id_to_complex_ids:
            bioent_id_to_complex_ids[biofact.bioentity_id].add(go_id_to_complex_id[biofact.bioconcept_id])
        else:
            bioent_id_to_complex_ids[biofact.bioentity_id] = set([go_id_to_complex_id[biofact.bioconcept_id]])

    edge_to_score = {}
    complex_id_to_scores = {}
    bioconcept_id_to_scores = {}
    for biofact in all_relevant_biofacts:
        complex_ids = [] if biofact.bioentity_id not in bioent_id_to_complex_ids else bioent_id_to_complex_ids[biofact.bioentity_id]
        bioconcept_id = biofact.bioconcept_id

        for complex_id in complex_ids:
            edge_to_score[(complex_id, bioconcept_id)] = 1 if (complex_id, bioconcept_id) not in edge_to_score else edge_to_score[(complex_id, bioconcept_id)] + 1

    for edge, score in edge_to_score.iteritems():
        if edge[0] in complex_id_to_scores:
            complex_id_to_scores[edge[0]].append(score)
        else:
            complex_id_to_scores[edge[0]] = [score]
        if edge[1] in bioconcept_id_to_scores:
            bioconcept_id_to_scores[edge[1]].append(score)
        else:
            bioconcept_id_to_scores[edge[1]] = [score]

    cutoff = 1
    node_count = len(complex_id_to_scores) + len(bioconcept_id_to_scores)
    edge_count = len(edge_to_score)

    biocon_ids_in_use = bioconcept_id_to_scores.keys()
    complex_ids_in_use = complex_id_to_scores.keys()
    edges_in_use = edge_to_score.keys()
    while node_count > 50 or edge_count > 250:
        cutoff = cutoff + 1
        biocon_ids_in_use = set([x for x, y in bioconcept_id_to_scores.iteritems() if len(y) > 1])
        complex_ids_in_use = set([x for x, y in complex_id_to_scores.iteritems() if len(y) > 1])
        edges_in_use = set([x for x, y in edge_to_score.iteritems() if y > cutoff])

        biocon_ids_in_use = set(x for x in biocon_ids_in_use if len([z for z in edges_in_use if z[1] == x]) > 1)
        complex_ids_in_use = set(x for x in complex_ids_in_use if len([z for z in edges_in_use if z[0] == x]) > 1)
        edges_in_use = set([x for x in edges_in_use if x[0] in complex_ids_in_use and x[1] in biocon_ids_in_use])

        node_count = len(complex_ids_in_use) + len(biocon_ids_in_use)
        edge_count = len(edges_in_use)

    if len(complex_ids_in_use) > 0:

        nodes = [create_complex_node(id_to_biocon[x], x==complex_id, max(complex_id_to_scores[x])) for x in complex_ids_in_use]
        nodes.extend([create_biocon_node(id_to_biocon[x], max(bioconcept_id_to_scores[x])) for x in biocon_ids_in_use])

        edges = [create_edge(x[0], x[1]) for x in edges_in_use]

        return {'nodes': nodes, 'edges': list(edges), 'max_cutoff': max([max(x) for x in complex_id_to_scores.values()]), 'min_cutoff':cutoff if len(complex_ids_in_use) == 1 else min([max(complex_id_to_scores[x]) for x in complex_ids_in_use if x != complex_id])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}
