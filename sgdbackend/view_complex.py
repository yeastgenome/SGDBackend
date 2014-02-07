from model_new_schema import create_format_name
from sgdbackend_query.query_auxiliary import get_biofacts, get_interactions_among

__author__ = 'kpaskov'

from sgdbackend_utils.cache import id_to_biocon, id_to_bioent


# -------------------------------Graph-----------------------------------------

def create_bioent_node(bioent, is_focus, gene_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'],
                    'sub_type':sub_type, 'type': 'BIOENTITY', 'gene_count':gene_count}}

def create_biocon_node(biocon_id, biocon_type, gene_count):
    if biocon_type == 'PHENOTYPE':
        return {'data':{'id':'BioconNode' + biocon_id, 'name':biocon_id, 'link': '/observable/' + create_format_name(biocon_id) + '/overview',
                    'sub_type':None, 'type': 'BIOCONCEPT', 'gene_count':gene_count}}
    else:
        biocon = id_to_biocon[biocon_id]
        return {'data':{'id':'BioconNode' + str(biocon['id']), 'name':biocon['display_name'], 'link': biocon['link'],
                    'sub_type':None if not 'go_aspect' in biocon else biocon['go_aspect'], 'type': 'BIOCONCEPT', 'gene_count':gene_count}}

def create_bioent_biocon_edge(bioent_id, biocon_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'BioconNode' + str(biocon_id)}}

def create_bioent_bioent_edge(bioent_id1, bioent_id2):
    return {'data':{'target': 'BioentNode' + str(bioent_id1), 'source': 'BioconNode' + str(bioent_id2)}}

def make_graph(biocon_id):

    #Get bioentities for complex
    bioentity_ids = [x.bioentity_id for x in get_biofacts('GO', biocon_id=id_to_biocon[biocon_id]['go_id'])]

    interactions = get_interactions_among('PHYSINTERACTION', bioentity_ids, 0)


    return {'nodes': [create_bioent_node(id_to_bioent[x]) for x in bioentity_ids], 'edges': [create_bioent_bioent_edge(x.bioentity1_id, x.bioentity2_id) for x in interactions]}
