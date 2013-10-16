'''
Created on Sep 20, 2013

@author: kpaskov
'''
from sgdbackend_query.query_bioent import get_domain_evidence
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_strain
from sgdbackend_utils.obj_to_json import domain_to_json

'''
-------------------------------Details---------------------------------------
''' 
def make_details(bioent_id):
    protein = id_to_bioent[bioent_id + 200000]
    domain_evidences = [x for x in get_domain_evidence(protein['id']) if x.domain.display_name != 'seg' ]
    return create_simple_table(domain_evidences, make_evidence_row) 

def make_evidence_row(domain_evidence): 
    return {    'start': domain_evidence.start,
                'end': domain_evidence.end,
                'evalue': domain_evidence.evalue,
                'status': domain_evidence.status,
                'date_of_run': domain_evidence.date_of_run,
                'protein': id_to_bioent[domain_evidence.protein_id],
                'domain': domain_to_json(domain_evidence.domain),
                'source': domain_evidence.source,
                'strain': id_to_strain[domain_evidence.strain_id]
                }