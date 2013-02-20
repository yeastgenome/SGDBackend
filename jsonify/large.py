'''
Created on Feb 19, 2013

@author: kpaskov
'''
from jsonify.mini import bioent_mini, reference_mini
from jsonify.small import biocon_small, bioent_biocon_small, phenoevidence_small, \
    bioent_small, biorel_small, interevidence_small, reference_small, allele_small

def biocon_large(biocon):
    basic_info = biocon_small(biocon)
    bioent_biocons = [bioent_biocon_small(bioent_biocon) for bioent_biocon in biocon.bioent_biocons]
    return {'basic_info':basic_info, 'bioent_biocons':bioent_biocons, 'bioent_biocon_count':len(bioent_biocons)} 

def bioent_biocon_large(bioent_biocon):
    basic_info = bioent_biocon_small(bioent_biocon)
    bioent = bioent_mini(bioent_biocon.bioentity)
    biocon = biocon_small(bioent_biocon.bioconcept)
    
    references = set([evidence.reference for evidence in bioent_biocon.evidences if evidence.reference is not None])
    json_references = [reference_mini(reference) for reference in references]
    json_evidences = [phenoevidence_small(evidence) for evidence in bioent_biocon.evidences]
    return {'basic_info':basic_info, 'bioent':bioent, 'biocon':biocon, 'evidences':json_evidences, 'references':json_references}  

def bioent_large(bioent):
    basic_info = bioent_small(bioent)
    
    interactions = [biorel_small(interaction) for interaction in bioent.biorelations if interaction.biorel_type == 'INTERACTION']
    phenotypes = [bioent_biocon_small(bioent_biocon) for bioent_biocon in bioent.bioent_biocons if bioent_biocon.bioconcept.biocon_type == 'PHENOTYPE']
        
    return {'basic_info':basic_info, 'genetic_position':bioent.genetic_position, 'interaction_count':len(interactions), 'interactions':interactions,
            'phenotype_count':len(phenotypes), 'phenotypes':phenotypes}

def biorel_large(biorel):
    basic_info = biorel_small(biorel)
            
    references = set([evidence.reference for evidence in biorel.evidences])
    json_references = [reference_mini(reference) for reference in references]
    json_genetic_evidences = [interevidence_small(evidence) for evidence in biorel.evidences if evidence.interaction_type == 'genetic']
    json_physical_evidences = [interevidence_small(evidence) for evidence in biorel.evidences if evidence.interaction_type == 'physical']
    
    return {'basic_info':basic_info, 'genetic_evidences':json_genetic_evidences, 'physical_evidences':json_physical_evidences, 'references': json_references}

def phenoevidence_large(evidence):
    basic_info = phenoevidence_small(evidence)
    properties = [(prop.type, prop.value, prop.description) for prop in evidence.properties]
    bioent_biocon = bioent_biocon_small(evidence.bioent_biocon)
    return {'basic_info':basic_info, 'properties':properties, 'biorel':None, 'bioent_biocon':bioent_biocon}

def interevidence_large(evidence):
    basic_info = interevidence_small(evidence)
    biorel = biorel_small(evidence.biorel)
    return {'basic_info':basic_info, 'biorel':biorel, 'bioent_biocon':None}

def reference_large(ref):
    basic_info = reference_small(ref)
    interaction_evidences = [interevidence_large(evidence) for evidence in ref.evidences if evidence.evidence_type == 'INTERACTION_EVIDENCE']
    phenotype_evidences = [phenoevidence_large(evidence) for evidence in ref.evidences if evidence.evidence_type == 'PHENOTYPE_EVIDENCE']

    return {'basic_info':basic_info, 'interaction_evidences':interaction_evidences, 'interaction_evidence_count':len(interaction_evidences),
            'phenotype_evidences':phenotype_evidences, 'phenotype_evidence_count':len(phenotype_evidences)} 

def allele_large(allele):
    basic_info = allele_small(allele)
    parent = bioent_mini(allele.parent)
    
    if parent is not None:
        basic_info['description'] = 'Allele of ' + parent['full_name']
    return {'basic_info':basic_info, 'parent':parent} 