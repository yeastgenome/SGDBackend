'''
Created on Sep 20, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Domainevidence
from sgdbackend_query import get_evidence
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_strain, id_to_bioitem, \
    id_to_source

'''
-------------------------------Details---------------------------------------
''' 
def make_details(bioent_id):
    protein = id_to_bioent[bioent_id + 200000]
    domain_evidences = [x for x in get_evidence(Domainevidence, bioent_id=protein['id']) if x.domain.display_name != 'seg' ]
    return create_simple_table(domain_evidences, make_evidence_row) 

def make_evidence_row(domain_evidence): 
    return {    'start': domain_evidence.start,
                'end': domain_evidence.end,
                'evalue': domain_evidence.evalue,
                'status': domain_evidence.status,
                'date_of_run': domain_evidence.date_of_run,
                'protein': id_to_bioent[domain_evidence.bioentity_id],
                'domain': id_to_bioitem[domain_evidence.domain_id],
                'source': id_to_source[domain_evidence.source_id],
                'strain': id_to_strain[domain_evidence.strain_id]
                }