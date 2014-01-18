'''
Created on Sep 23, 2013

@author: kpaskov
'''

from model_new_schema.evidence import Bindingevidence
from sgdbackend_query import get_evidence
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent
from sgdbackend_utils.obj_to_json import minimize_json, evidence_to_json

'''
-------------------------------Details---------------------------------------
'''
def make_details(locus_id=None, reference_id=None):
    binding_site_evidences = get_evidence(Bindingevidence, bioent_id=locus_id, reference_id=reference_id)

    if binding_site_evidences is None:
        return {'Error': 'Too much data to display.'}

    return create_simple_table(binding_site_evidences, make_evidence_row) 

def make_evidence_row(binding_evidence): 
    obj_json = evidence_to_json(binding_evidence).copy()
    obj_json['bioentity'] = minimize_json(id_to_bioent[binding_evidence.bioentity_id], include_format_name=True)
    obj_json['total_score'] = binding_evidence.total_score
    obj_json['expert_confidence'] = binding_evidence.expert_confidence
    obj_json['img_url'] = binding_evidence.link
    obj_json['motif_id'] = binding_evidence.motif_id
    return obj_json