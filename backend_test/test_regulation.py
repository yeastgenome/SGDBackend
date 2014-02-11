'''
Created on Jul 10, 2013

@author: kpaskov
'''
from backend_test import check_evidence, check_obj, check_reference, \
    check_biocon
import json

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
            check_reference(reference)
                
def test_regulation_details_structure(model, identifier='GAL4'):
    response = json.loads(model.regulation_details(identifier))
    assert response is not None
    
    for entry in response:
        check_evidence(entry)
        assert 'bioentity1' in entry
        assert 'bioentity2' in entry
        assert 'conditions' in entry
        
        check_obj(entry['bioentity1'])
        check_obj(entry['bioentity2'])
        
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
        
def test_regulation_target_enrichment_structure(model, identifier='ADF1'):
    response = json.loads(model.regulation_target_enrichment(identifier))
    assert response is not None
    
    for entry in response:
        assert 'go' in entry
        assert 'match_count' in entry
        assert 'pvalue' in entry
        check_biocon(entry['go'])
        
   
        