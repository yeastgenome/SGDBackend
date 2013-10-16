'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_strain, check_bioent_extended, \
    check_biocon_extended, check_reference_extended, check_experiment
import json
import pytest

slow = pytest.mark.slow

def test_protein_domain_details_structure(model, identifier='GAL4'):
    response = json.loads(model.protein_domain_details(identifier))
    assert response is not None
    for entry in response:
        assert 'status' in entry
        assert 'start' in entry
        assert 'domain' in entry
        assert 'end' in entry
        assert 'source' in entry
        assert 'strain' in entry
        assert 'date_of_run' in entry
        assert 'evalue' in entry
        assert 'protein' in entry
    
        domain = entry['domain']
        assert 'interpro_description' in domain
        assert 'display_name' in domain
        assert 'description' in domain
        assert 'format_name' in domain
        assert 'source' in domain
        assert 'link' in domain
        assert 'interpro_id' in domain
        
        check_strain(entry['strain'])
        check_bioent_extended(entry['protein'])
    
def test_all_bioconcepts_structure(model, min_id=50000000, max_id=50000200):
    response = json.loads(model.all_bioconcepts(min_id, max_id))
    assert response is not None
    for entry in response:
        check_biocon_extended(entry)
     
def test_bioconcept_list_structure(model, biocon_ids=[50001220, 50001050, 50001069]):
    response = json.loads(model.bioconcept_list(biocon_ids))
    assert response is not None
    assert len(response) == 3
    for entry in response:
        check_biocon_extended(entry)
        
def test_binding_site_details_structure(model, identifier='GAL4'):
    response = json.loads(model.binding_site_details(identifier))
    assert response is not None
    for entry in response:
        assert 'source' in entry
        assert 'expert_confidence' in entry
        assert 'experiment' in entry
        assert 'reference' in entry
        assert 'bioent' in entry
        assert 'total_score' in entry
        assert 'motif_id' in entry
        assert 'img_url' in entry
        
        check_reference_extended(entry['reference'])
        check_bioent_extended(entry['bioent'])
        check_experiment(entry['experiment'])
        
def test_all_disambigs_structure(model, min_id=100, max_id=100):
    response = json.loads(model.all_disambigs(min_id, max_id))
    assert response is not None
    for entry in response:
        assert 'disambig_key' in entry
        assert 'subclass_type' in entry
        assert 'disambig_id' in entry
        assert 'class_type' in entry
        assert 'identifier' in entry
