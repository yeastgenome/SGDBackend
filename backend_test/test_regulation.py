'''
Created on Jul 10, 2013

@author: kpaskov
'''
from backend_test import check_reference_extended, check_reference, check_strain, \
    check_experiment, check_bioent
import json
import pytest

slow = pytest.mark.slow

def test_regulation_overview_structure(model, identifier='GAL4'):
    response = json.loads(model.regulation_overview(identifier))
    assert response is not None
    assert 'regulator_count' in response
    assert 'target_count' in response
        
    if 'paragraph' in response:
        paragraph = response['paragraph']
        assert 'text' in paragraph
        assert 'references' in paragraph
        for reference in paragraph['references']:
            check_reference_extended(reference)
                
def test_regulation_details_structure(model, identifier='GAL4'):
    response = json.loads(model.regulation_details(identifier))
    assert response is not None
    assert 'regulators' in response
    assert 'targets' in response
    
    for entry in response['regulators']:
        assert 'reference' in entry
        assert 'source' in entry
        assert 'strain' in entry
        assert 'experiment' in entry
        assert 'bioent1' in entry
        assert 'bioent2' in entry
        assert 'conditions' in entry
        
        check_reference(entry['reference'])
        check_strain(entry['strain'])
        check_experiment(entry['experiment'])
        check_bioent(entry['bioent1'])
        check_bioent(entry['bioent2'])
        
    for entry in response['targets']:
        assert 'reference' in entry
        assert 'source' in entry
        assert 'strain' in entry
        assert 'experiment' in entry
        assert 'bioent1' in entry
        assert 'bioent2' in entry
        assert 'conditions' in entry
        
        check_reference(entry['reference'])
        check_strain(entry['strain'])
        check_experiment(entry['experiment'])
        check_bioent(entry['bioent1'])
        check_bioent(entry['bioent2'])
        
def test_regulation_graph_structure(model, identifier='GAL4'):
    response = json.loads(model.regulation_graph(identifier))
    assert response is not None
    assert 'edges' in response
    assert 'nodes' in response
    assert 'max_evidence_cutoff' in response
    assert 'max_regulator_cutoff' in response
    assert 'max_target_cutoff' in response
    
    for entry in response['edges']:
        assert 'data' in entry
        edge_data = entry['data']
        assert 'source' in edge_data
        assert 'target' in edge_data
        assert 'evidence' in edge_data
        
    for entry in response['nodes']:
        assert 'data' in entry
        node_data = entry['data']
        assert 'class_type' in node_data
        assert 'evidence' in node_data
        assert 'link' in node_data
        assert 'id' in node_data
        assert 'sub_type' in node_data
        assert 'name' in node_data
        
def test_regulation_references(model, identifier='GAL4'):
    response = json.loads(model.regulation_references(identifier))
    assert response is not None
    for entry in response:
        check_reference_extended(entry)
        