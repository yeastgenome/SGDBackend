'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Phenotypeevidence
from sgdbackend_query import get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_biofacts
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent, id_to_reference, \
    id_to_source, id_to_experiment, id_to_strain
from sgdbackend_utils.obj_to_json import condition_to_json
'''
-------------------------------Overview---------------------------------------
'''  

def make_overview(bioent_id):
    biofacts = get_biofacts('PHENOTYPE', bioent_id=bioent_id)

    return {'count': len(biofacts)}

    
'''
-------------------------------Details---------------------------------------
'''
    
def make_details(locus_id=None, phenotype_id=None):
    phenoevidences = get_evidence(Phenotypeevidence, bioent_id=locus_id, biocon_id=phenotype_id)
    
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in phenoevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
            
    tables = create_simple_table(phenoevidences, make_evidence_row, id_to_conditions=id_to_conditions)
        
    return tables  

def make_evidence_row(phenoevidence, id_to_conditions): 
    bioentity_id = phenoevidence.bioentity_id
    bioconcept_id = phenoevidence.bioconcept_id
    reference_id = phenoevidence.reference_id 
    source_id = phenoevidence.source_id
    experiment_id = phenoevidence.experiment_id
    strain_id = phenoevidence.strain_id
    conditions = None if phenoevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[phenoevidence.id]]
        
    return {'bioentity': id_to_bioent[bioentity_id],
            'bioconcept': id_to_biocon[bioconcept_id],
            'conditions': conditions,
            'reference': id_to_reference[reference_id],
            'source': id_to_source[source_id],
            'experiment': id_to_experiment[experiment_id],
            'source': id_to_strain[strain_id]
            }