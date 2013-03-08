'''
Created on Mar 6, 2013

@author: kpaskov
'''
from string import lower
def add_link(name, link):
    return '<a href="' + link + '">' + name + '</a>'

link_symbol = unichr(8213)

#Bioentity links
def bioent_link(bioent):
    return '/bioent/' + bioent.official_name
def bioent_all_phenotypes_link(bioent):
    return '/bioent_biocon/phenotype=' + bioent.official_name
def bioent_all_interactions_link(bioent):
    return '/biorel/interaction=' + bioent.official_name
def bioent_all_go_link(bioent):
    return '/bioent_biocon/go=' + bioent.official_name

def bioent_graph_link(bioent):
    return bioent.link + '/graph'
def bioent_wiki_link(bioent):
    return 'http://wiki.yeastgenome.org/index.php/' + bioent.official_name

def bioent_all_biorel_link(bioent):
    return bioent.link + '/biorel'
def bioent_all_biocon_link(bioent):
    return bioent.link + '/biocon'


#Biorelation links
def biorel_link(biorel):
    return '/biorel/' + lower(biorel.biorel_type) + '=' + biorel.official_name
def biorel_evidence_link(biorel):
    return biorel.link + '/evidence'

#BioentBiocon links
def bioent_biocon_link(bioent_biocon):
    return '/bioent_biocon/' + lower(bioent_biocon.biocon_type) + '=' + bioent_biocon.official_name
def bioent_biocon_evidence_link(bioent_biocon):
    return bioent_biocon.link + '/evidence'
def bioent_biocon_reference_link(bioent_biocon):
    return bioent_biocon.link + '/reference'

#Bioconcept links
def biocon_link(biocon):
    return '/biocon/' + lower(biocon.biocon_type) + '=' + biocon.official_name
def biocon_all_bioent_link(biocon):
    return biocon.link + '/bioent'

#Reference links
def reference_link(reference):
    link_str = reference.pubmed_id
    if link_str is None:
        link_str = reference.dbxref_id
    if link_str is None:
        link_str = str(reference.id)
    return '/reference/' + str(link_str)

#Misc links
def allele_link(allele):
    return '/allele/' + allele.official_name