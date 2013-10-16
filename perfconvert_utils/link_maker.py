'''
Created on Mar 6, 2013

@author: kpaskov
'''

backend_start = None
frontend_start = ''

def add_format_name_params(link, key_to_format_name):
    params = {}
    for key, format_name in key_to_format_name.iteritems():
        if format_name is not None:
            params[key] = format_name
        
    full_link = backend_start + link + '&'.join([key + '=' + value for key, value in params.iteritems()])
    return full_link

#Disambig Links
def all_disambig_link(min_id, max_id):
    return backend_start + '/all_disambigs?min=' + str(min_id) + '&max=' + str(max_id)

#Bioentity Links
def all_bioentity_link(min_id, max_id):
    return backend_start + '/all_bioentities?min=' + str(min_id) + '&max=' + str(max_id)
def locustabs_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/tabs'

#Reference Links
def all_reference_link(min_id, max_id):
    return backend_start + '/all_references?min=' + str(min_id) + '&max=' + str(max_id)
def all_bibentry_link(min_id, max_id):
    return backend_start + '/all_bibentries?min=' + str(min_id) + '&max=' + str(max_id)

#Bioconcept 
def all_bioconcept_link(min_id, max_id):
    return backend_start + '/all_bioconcepts?min=' + str(min_id) + '&max=' + str(max_id)

#Interaction Links
def interaction_overview_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/interaction_overview'
def interaction_details_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/interaction_details'
def interaction_graph_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/interaction_graph'
def interaction_resources_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/interaction_resources'
def interaction_references_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/interaction_references'

#Literature Links
def literature_overview_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/literature_overview'
def literature_details_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/literature_details'
def literature_graph_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/literature_graph'

#Regulation Links
def regulation_overview_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/regulation_overview'
def regulation_details_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/regulation_details'
def regulation_graph_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/regulation_graph'
def regulation_references_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/regulation_references'

#Go Links
def go_references_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/go_references'

#Phenotype Links
def phenotype_references_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/phenotype_references'

#Protein Links
def protein_domain_details_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/protein_domain_details'
def binding_site_details_link(bioent_id):
    return backend_start + '/locus/' + str(bioent_id) + '/binding_site_details'
