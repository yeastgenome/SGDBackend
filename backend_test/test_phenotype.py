'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_biocon_extended
import json

def test_phenotype_structure(model, identifier='abnormal|endoplasmic_reticulum_morphology|null'):
    response = json.loads(model.phenotype(identifier))
    assert response is not None
    check_biocon_extended(response)
