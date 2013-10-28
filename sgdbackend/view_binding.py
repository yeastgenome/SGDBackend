'''
Created on Sep 23, 2013

@author: kpaskov
'''

from model_new_schema.evidence import Bindingevidence
from sgdbackend_query import get_evidence
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_reference, id_to_bioent, \
    id_to_experiment, id_to_source

'''
-------------------------------Details---------------------------------------
'''
def make_details(bioent_id):
    binding_site_evidences = get_evidence(Bindingevidence, bioent_id=bioent_id)
    return create_simple_table(binding_site_evidences, make_evidence_row) 

def make_evidence_row(binding_evidence): 
    bioentity_id = binding_evidence.bioentity_id
    reference_id = binding_evidence.reference_id 
    experiment_id = binding_evidence.experiment_id
    
    return {'bioent': id_to_bioent[bioentity_id],
                'reference': None if reference_id is None else id_to_reference[reference_id],
                'experiment': None if experiment_id is None else id_to_experiment[experiment_id],
                'source': id_to_source[binding_evidence.source_id],
                'total_score': binding_evidence.total_score,
                'expert_confidence': binding_evidence.expert_confidence,
                'img_url': binding_evidence.link,
                'motif_id': binding_evidence.motif_id
                }