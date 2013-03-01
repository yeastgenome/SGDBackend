'''
Created on Feb 19, 2013

@author: kpaskov
'''
from jsonify.mini import bioent_mini, reference_mini, interevidence_mini
from jsonify.small import biocon_small, bioent_biocon_small, bioent_small, \
    biorel_small, phenoevidence_small, interevidence_small, reference_small, \
    allele_small, phenoevidence_mid, all_biorel_small
from model_new_schema.biorelation import Biorelation


def biocon_large(biocon):
    basic_info = biocon_small(biocon)
    return {'basic_info':basic_info, 'genes_link':basic_info['link'] + '/genes'} 

def bioent_biocon_large(bioent_biocon):
    basic_info = bioent_biocon_small(bioent_biocon)
    bioent = bioent_mini(bioent_biocon.bioentity)
    biocon = biocon_small(bioent_biocon.bioconcept)

    return {'basic_info':basic_info, 'bioent':bioent, 'biocon':biocon, 'evidence_link':basic_info['link'] + '/evidence', 'references_link':basic_info['link'] + '/references'}  

def bioent_large(bioent):
    basic_info = bioent_small(bioent)
    
        
    return {'basic_info':basic_info, 'genetic_position':bioent.genetic_position, 'interaction_count':0, 'interaction_link':basic_info['link'] + '/interactions',
            'phenotype_count':0, 'phenotype_link':basic_info['link'] + '/phenotypes', 'all_interactions_link':'/biorel/' + bioent.name}

def biorel_large(biorel):
    if isinstance(biorel, Biorelation):
        basic_info = biorel_small(biorel)
    else:
        basic_info = all_biorel_small(biorel)
    return {'basic_info':basic_info, 'genetic_evidence_link':basic_info['link'] + '/genetic_evidence', 'physical_evidence_link':basic_info['link'] + '/physical_evidence', 'references_link': basic_info['link'] + '/references'}

def phenoevidence_large(evidence):
    basic_info = phenoevidence_small(evidence)
    return {'basic_info':basic_info}

def interevidence_large(evidence):
    basic_info = interevidence_small(evidence)
    return {'basic_info':basic_info}

def reference_large(ref):
    basic_info = reference_small(ref)
    return {'basic_info':basic_info, 'interactions_link':basic_info['link'] + '/interactions',
            'phenotypes_link':basic_info['link'] + '/phenotypes'} 

def allele_large(allele):
    basic_info = allele_small(allele)
    parent = bioent_mini(allele.parent)
    
    if parent is not None:
        basic_info['description'] = 'Allele of ' + parent['full_name']
    return {'basic_info':basic_info, 'parent':parent} 