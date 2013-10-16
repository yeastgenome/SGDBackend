'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_reference_extended
import pytest

slow = pytest.mark.slow

def test_literature_overview_structure(model, identifier='YFL039C'):
    response = model.literature_overview(identifier)
    assert response is not None
    assert 'GENINTERACTION' in response
    assert 'PHYSINTERACTION' in response
    assert 'REGULATION' in response
    assert 'REVIEW_LITERATURE' in response
    assert 'PHENOTYPE' in response
    assert 'ADDITIONAL_LITERATURE' in response
    assert 'GO' in response
    assert 'PRIMARY_LITERATURE' in response
    assert 'Total' in response
    
def test_literature_details_structure(model, identifier='YFL039C'):
    response = model.literature_details(identifier)
    assert response is not None
    assert 'primary' in response
    assert 'additional' in response
    assert 'reviews' in response
    
    for entry in response['primary']:
        check_reference_extended(entry)
    
    for entry in response['additional']:
        check_reference_extended(entry)
        
    for entry in response['reviews']:
        check_reference_extended(entry)
     
def test_literature_graph_structure(model, identifier='YFL039C'):
    response = model.literature_graph(identifier)
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
    
    for node_entry in response['nodes']:
        assert 'data' in node_entry
        node_data = node_entry['data']
        assert 'type' in node_data
        assert 'sub_type' in node_data
        assert 'link' in node_data
        assert 'id' in node_data
        assert 'name' in node_data
        
    for edge_entry in response['edges']:
        assert 'data' in edge_entry
        edge_data = edge_entry['data']
        assert 'source' in edge_data
        assert 'target' in edge_data