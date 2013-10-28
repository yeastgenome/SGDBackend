'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_biocon_extended
import json

def test_go_structure(model, identifier='GO:1553'):
    response = json.loads(model.go(identifier))
    assert response is not None
    check_biocon_extended(response)
    
def test_go_enrichment_structure(model, bioent_ids=[7361, 7372, 48, 2901]):
    response = json.loads(model.go_enrichment(bioent_ids))
    assert response is not None
