'''
Created on Mar 6, 2013

@author: kpaskov
'''
from string import lower
def add_link(name, link):
    return '<a href="' + link + '">' + name + '</a>'

link_symbol = unichr(8213)

def add_official_name_params(link, key_to_obj):
    params = {}
    for key, obj in key_to_obj.iteritems():
        if obj is not None:
            params[key] = obj.official_name
    full_link = link + '&'.join([key + '=' + value for key, value in params.iteritems()])
    return full_link

#Bioentity links

#Bioconcept links
def go_overview_table_link(biocon=None, bioent=None):
    overview_link = add_official_name_params('/go_overview_table?', {'bioent_name':bioent, 'biocon_name': biocon})
    return overview_link

def go_evidence_table_link(biocon=None, bioent=None):
    evidence_link = add_official_name_params('/go_evidence_table?', {'bioent_name':bioent, 'biocon_name': biocon})
    return evidence_link

def go_evidence_link(biocon=None, bioent=None):
    evidence_link = add_official_name_params('/go_evidence?', {'bioent_name':bioent, 'biocon_name': biocon})
    return evidence_link

#Bioentity links
def bioent_link(bioent):
    return '/bioent/' + bioent.official_name
def bioent_all_link(bioent, bio_type, link_type):
    return '/' + bio_type + '/' + link_type + '=' + bioent.official_name

def bioent_interaction_graph_link(bioent):
    return bioent.link + '/interaction_graph'
def bioent_go_graph_link(bioent):
    return bioent.link + '/go_graph'
def bioent_wiki_link(bioent):
    return 'http://wiki.yeastgenome.org/index.php/' + bioent.official_name

def bioent_all_biorel_link(bioent):
    return bioent.link + '/biorel'
def bioent_all_biocon_link(bioent):
    return bioent.link + '/biocon'
def bioent_go_link(bioent):
    return bioent.link + '/go'
def bioent_phenotype_link(bioent):
    return bioent.link + '/phenotype'
def bioent_interaction_link(bioent):
    return bioent.link + '/interaction'

#Biorelation links
def biorel_link(biorel):
    return '/biorel/' + lower(biorel.biorel_type) + '=' + biorel.official_name

#BioentBiocon links
def bioent_biocon_link(bioent_biocon):
    return '/bioent_biocon/' + lower(bioent_biocon.biocon_type) + '=' + bioent_biocon.official_name

def bioent_biocon_reference_link(bioent_biocon):
    return bioent_biocon.link + '/reference'

#Bioconcept links
def biocon_link(biocon):
    return '/' + lower(biocon.biocon_type) + '/' + biocon.link_name
def biocon_all_bioent_link(biocon):
    return evidence_link(biocon=biocon)

#Reference links
def reference_link(reference):
    return '/reference/' + reference.official_name

def reference_evidence_link(reference):
    return reference.link + '/evidence'
def reference_phenotype_link(reference):
    return reference.link + '/phenotype'
def reference_go_link(reference):
    return reference.link + '/go'
def reference_interaction_link(reference):
    return reference.link + '/interaction'

#Misc links
def allele_link(allele):
    return '/allele/' + allele.official_name