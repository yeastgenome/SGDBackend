'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_evidence, check_obj, check_condition, \
    check_biocon
import json

def test_go_structure(model, identifier='GO:0001553'):
    response = json.loads(model.go(identifier))
    assert response is not None
    check_biocon(response)

#def test_go_enrichment_structure(model, bioent_ids=[3485, 5783, 4131, 3306, 4258, 6159, 2615, 5609, 1633, 6917]):
#    response = json.loads(model.go_enrichment(bioent_ids))
#    assert response is not None
    
def test_go_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.go_overview(identifier=identifier))
    assert response is not None
    assert 'go_slim' in response
    assert 'date_last_reviewed' in response
    
def test_go_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.go_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'bioconcept' in entry
        assert 'bioentity' in entry
        assert 'conditions' in entry
        assert 'qualifier' in entry

        check_obj(entry['bioconcept'])
        check_obj(entry['bioentity'])
        for cond in entry['conditions']:
            check_condition(cond)
