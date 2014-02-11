'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_url, check_evidence, check_obj
import json

def test_interaction_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_overview(identifier=identifier))
    assert response is not None
    assert 'gen_circle_size' in response
    assert 'phys_circle_size' in response
    assert 'circle_distance' in response
    assert 'num_gen_interactors' in response
    assert 'num_phys_interactors' in response
    assert 'num_both_interactors' in response
    
def test_interaction_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'bioentity1' in entry
        assert 'bioentity2' in entry
        assert 'bait_hit' in entry
        assert 'interaction_type' in entry
        assert 'annotation_type' in entry
        
        check_obj(entry['bioentity1'])
        check_obj(entry['bioentity2'])
        
        if entry['interaction_type'] == 'Genetic':
            assert 'phenotype' in entry
            check_obj(entry['phenotype'])
            assert 'modification' not in entry
        else:
            assert 'modification' in entry
            assert 'phenotype' not in entry
     
def test_interaction_graph_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_graph(identifier=identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
    assert 'min_evidence_cutoff' in response
    assert 'max_evidence_cutoff' in response
    assert 'max_phys_cutoff' in response
    assert 'max_gen_cutoff' in response
    
    assert len(response['nodes']) < 100
    for node_entry in response['nodes']:
        assert 'data' in node_entry
        node_data = node_entry['data']
        assert 'sub_type' in node_data
        assert 'name' in node_data
        assert 'evidence' in node_data
        assert 'genetic' in node_data
        assert 'link' in node_data
        assert 'id' in node_data
        assert 'physical' in node_data
        
    assert len(response['edges']) < 500
    for edge_entry in response['edges']:
        assert 'data' in edge_entry
        edge_data = edge_entry['data']
        assert 'source' in edge_data
        assert 'class_type' in edge_data
        assert 'evidence' in edge_data
        assert 'target' in edge_data
     
def test_interaction_resources_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_resources(identifier=identifier))
    assert response is not None
    for entry in response:
        check_url(entry)
