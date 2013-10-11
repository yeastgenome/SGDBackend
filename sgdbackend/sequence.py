'''
Created on Sep 23, 2013

@author: kpaskov
'''

from sgdbackend_utils.cache import get_cached_bioent, get_cached_reference, \
    get_cached_experiment
from sgdbackend_utils import create_simple_table
from sgdbackend_query.query_evidence import get_binding_site_evidence   

'''
-------------------------------Details---------------------------------------
'''
def make_details(bioent_id):
    binding_site_evidences = get_binding_site_evidence(bioent_id)
    return create_simple_table(binding_site_evidences, make_evidence_row) 

def make_evidence_row(binding_evidence): 
    bioentity_id = binding_evidence.bioentity_id
    reference_id = binding_evidence.reference_id 
    experiment_id = binding_evidence.experiment_id
    
    reference = None
    if reference_id is not None:
        reference = get_cached_reference(reference_id)
    
    return {'bioent': get_cached_bioent(bioentity_id),
                'reference': reference,
                'experiment': get_cached_experiment(experiment_id),
                'source': binding_evidence.source,
                'total_score': binding_evidence.total_score,
                'expert_confidence': binding_evidence.expert_confidence,
                'img_url': binding_evidence.img_url,
                'motif_id': binding_evidence.motif_id
                }