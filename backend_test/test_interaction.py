'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_reference, check_strain, check_bioent, \
    check_experiment, check_biocon, check_url
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
    response = json.loads(model.interaction_details(identifier=identifier))
    assert response is not None
    for entry in response:
        assert 'direction' in entry
        assert 'reference' in entry
        assert 'strain' in entry
        assert 'bioent1' in entry
        assert 'bioent2' in entry
        assert 'interaction_type' in entry
        assert 'note' in entry
        assert 'source' in entry
        assert 'experiment' in entry
        assert 'annotation_type' in entry
        
        check_reference(entry['reference'])
        check_strain(entry['strain'])
        check_bioent(entry['bioent1'])
        check_bioent(entry['bioent2'])
        check_experiment(entry['experiment'])
        
        if entry['interaction_type'] == 'Genetic':
            assert 'phenotype' in entry
            check_biocon(entry['phenotype'])
        else:
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
    assert 'max_both_cutoff' in response
    
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
        assert 'genetic' in edge_data
        assert 'evidence' in edge_data
        assert 'target' in edge_data
        assert 'physical' in edge_data
     
def test_interaction_resources_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_resources(identifier=identifier))
    assert response is not None
    for entry in response:
        check_url(entry)
