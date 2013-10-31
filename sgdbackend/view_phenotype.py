'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Phenotypeevidence
from sgdbackend_query import get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_biofacts
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent
from sgdbackend_utils.obj_to_json import condition_to_json, minimize_json, \
    evidence_to_json
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
    conditions = [] if phenoevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[phenoevidence.id]]
        
    obj_json = evidence_to_json(phenoevidence)
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['bioconcept'] = minimize_json(id_to_biocon[bioconcept_id])
    obj_json['conditions'] = conditions
    return obj_json