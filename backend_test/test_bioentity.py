'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_bioent_extended
import json

def test_all_bioentities_structure(model, min_id=0, max_id=100):
    response = json.loads(model.all_bioentities(min_id, max_id))
    assert response is not None
    for entry in response:
        check_bioent_extended(entry)
    
def test_bioentity_list_structure(model, bioent_ids=[25, 26, 27, 28, 29]):
    response = json.loads(model.bioentity_list(bioent_ids))
    assert response is not None
    assert len(response) == 5
    for entry in response:
        check_bioent_extended(entry)
     
def test_locus_structure(model, identifier='YFL039C'):
    response = json.loads(model.locus(identifier))
    assert response is not None
    check_bioent_extended(response)
    
def test_locustabs_structure(model, identifier='YFL039C'):
    response = json.loads(model.locustabs(identifier))
    assert response is not None
    assert 'protein_tab' in response
    assert 'interaction_tab' in response
    assert 'bioentity_id' in response
    assert 'summary_tab' in response
    assert 'go_tab' in response
    assert 'expression_tab' in response
    assert 'phenotype_tab' in response
    assert 'regulation_tab' in response
    assert 'history_tab' in response
    assert 'literature_tab' in response
    assert 'wiki_tab' in response