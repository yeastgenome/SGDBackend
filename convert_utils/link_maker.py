'''
Created on Mar 6, 2013

@author: kpaskov
'''

#Bioconcept links
def biocon_link(biocon_type, format_name):
    if biocon_type == 'GO':
        return 'http://www.yeastgenome.org/cgi-bin/GO/goTerm.pl?goid=' + format_name
    return None
    
#Bioentity links
def bioent_link(bioent_type, format_name):
    #return '/%s/%s' % (bioent_type, format_name)
    return 'http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=' + format_name

#Chemical links
def chemical_link(format_name):
    #return '/chemical/' +format_name
    return None

#Reference links
def reference_link(format_name):
    #return '/reference/' + format_name
    try:
        int(format_name)
        return 'http://www.yeastgenome.org/cgi-bin/reference/reference.pl?pmid=' + format_name
    except ValueError:
        return 'http://www.yeastgenome.org/cgi-bin/reference/reference.pl?dbid=' + format_name

#Author links
def author_link(format_name):
    #return '/author/' + format_name
    return None

#Experiment links
def experiment_link(format_name):
    #return '/experiment/' + format_name
    return None

#Strain links
def strain_link(format_name):
    #return '/strain/' + format_name
    return None

#Allele links
def allele_link(format_name):
    #return '/allele/' + format_name
    return None