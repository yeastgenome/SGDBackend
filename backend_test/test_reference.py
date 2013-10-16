'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_reference_extended
import pytest

slow = pytest.mark.slow

def test_reference_structure(model, identifier='769'):
    response = model.reference(identifier)
    assert response is not None
    check_reference_extended(response)
    
def test_all_references_structure(model, min_id=100, max_id=200):
    response = model.all_references(min_id, max_id)
    assert response is not None
    for entry in response:
        check_reference_extended(entry)
    
def test_all_bibentries_structure(model, min_id=100, max_id=200):
    response = model.all_bibentries(min_id, max_id)
    assert response is not None
    for entry in response:
        assert entry is not None
    
def test_reference_list_structure(model, reference_ids=[769, 341, 117]):
    response = model.reference_list(reference_ids)
    assert response is not None
    assert len(response) == 3
    for entry in response:
        assert entry is not None