'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_evidence, check_obj, check_biocon
import json

def test_protein_domain_details_structure(model, identifier='GAL4'):
    response = json.loads(model.protein_domain_details(identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'domain' in entry
        assert 'protein' in entry
        assert 'status' in entry
        assert 'start' in entry
        assert 'end' in entry
        assert 'date_of_run' in entry
        assert 'evalue' in entry
        assert 'domain_description' in entry
    
        check_obj(entry['domain'])
        check_obj(entry['protein'])
        
def test_binding_site_details_structure(model, identifier='GAL4'):
    response = json.loads(model.binding_site_details(identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'bioentity' in entry
        assert 'expert_confidence' in entry
        assert 'total_score' in entry
        assert 'motif_id' in entry
        assert 'img_url' in entry
        
        check_obj(entry['bioentity'])