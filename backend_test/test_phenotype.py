'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_biocon_extended, check_reference_extended
import pytest

slow = pytest.mark.slow

def test_phenotype_structure(model, identifier='60001411'):
    response = model.phenotype(identifier)
    assert response is not None
    check_biocon_extended(response)
    
def test_phenotype_references(model, identifier='YFL039C'):
    response = model.phenotype_references(identifier)
    assert response is not None
    for entry in response:
        check_reference_extended(entry)