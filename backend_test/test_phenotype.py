'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_biocon, check_evidence, check_obj
import json

def test_phenotype_structure(model, identifier='955'):
    response = json.loads(model.phenotype(identifier))
    assert response is not None
    check_biocon(response)

def test_phenotype_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_overview(identifier=identifier))
    assert response is not None
    assert 'count' in response
    
def test_phenotype_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'bioconcept' in entry
        assert 'bioentity' in entry
        assert 'conditions' in entry
        
        check_obj(entry['bioconcept'])
        check_obj(entry['bioentity'])