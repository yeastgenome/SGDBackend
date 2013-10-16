'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_reference_extended, check_biocon_extended
import pytest

slow = pytest.mark.slow

def test_go_structure(model, identifier='1881'):
    response = model.go(identifier)
    assert response is not None
    check_biocon_extended(response)
    
def test_go_references(model, identifier='YFL039C'):
    response = model.go_references(identifier)
    assert response is not None
    for entry in response:
        check_reference_extended(entry)
    
@slow
def test_go_enrichment_structure(model, bioent_format_names=['YFL039C', 'YGR002C', 'YJL184W', 'YMR292W']):
    response = model.go_enrichment(bioent_format_names)
    assert response is not None
