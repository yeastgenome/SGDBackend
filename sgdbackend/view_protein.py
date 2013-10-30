'''
Created on Sep 20, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Domainevidence
from sgdbackend_query import get_evidence
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_bioitem
from sgdbackend_utils.obj_to_json import minimize_json, evidence_to_json

'''
-------------------------------Details---------------------------------------
''' 
def make_details(protein_id):
    domain_evidences = [x for x in get_evidence(Domainevidence, bioent_id=protein_id) if x.domain.display_name != 'seg' ]
    return create_simple_table(domain_evidences, make_evidence_row) 

def make_evidence_row(domain_evidence): 
    obj_json = evidence_to_json(domain_evidence)
    obj_json['protein'] = minimize_json(id_to_bioent[domain_evidence.bioentity_id])
    obj_json['domain'] = minimize_json(id_to_bioitem[domain_evidence.domain_id])
    obj_json['domain_description'] = id_to_bioitem[domain_evidence.domain_id]['description']
    obj_json['start'] = domain_evidence.start
    obj_json['end'] = domain_evidence.end
    obj_json['evalue'] = domain_evidence.evalue
    obj_json['status'] = domain_evidence.status
    obj_json['date_of_run'] = domain_evidence.date_of_run
    return obj_json