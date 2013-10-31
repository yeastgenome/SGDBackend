'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_reference
import json

def test_reference_structure(model, identifier='178'):
    response = json.loads(model.reference(identifier))
    assert response is not None
    check_reference(response)
    
def test_reference_list_structure(model, reference_ids=[182, 360, 364]):
    response = json.loads(model.reference_list(reference_ids))
    assert response is not None
    assert len(response) == 3
    for entry in response:
        assert entry is not None