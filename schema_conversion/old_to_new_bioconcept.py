'''
Created on Feb 27, 2013

@author: kpaskov
'''

def experiment_property_to_phenoevidence_property(experiment_property):
    from model_new_schema.evidence import PhenoevidenceProperty
    
    new_phenoevidence_property = PhenoevidenceProperty(experiment_property.type, experiment_property.value, experiment_property.description, evidence_id=experiment_property.id)
    return new_phenoevidence_property
