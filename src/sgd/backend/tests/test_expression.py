import json
import pytest

from src.sgd.backend.tests import check_url, check_evidence, check_obj
from src.sgd.backend.tests.test_basic import check_dataset

__author__ = 'kpaskov'

def test_expression_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.expression_details(locus_identifier=identifier))
    assert response['overview'] is not None

def test_expression_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.expression_details(locus_identifier=identifier))
    assert response is not None
    for entry in response['datasets']:
        check_dataset(entry)

def test_expression_graph_structure(model, identifier='YFL039C'):
    response = json.loads(model.expression_graph(locus_identifier=identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
    assert 'min_coeff' in response
    assert 'max_coeff' in response

    assert len(response['nodes']) < 100
    for node_entry in response['nodes']:
        assert 'data' in node_entry
        node_data = node_entry['data']
        assert 'sub_type' in node_data
        assert 'name' in node_data
        assert 'type' in node_data
        assert 'link' in node_data
        assert 'id' in node_data

    assert len(response['edges']) < 500
    for edge_entry in response['edges']:
        assert 'data' in edge_entry
        edge_data = edge_entry['data']
        assert 'source' in edge_data
        assert 'class_type' in edge_data
        assert 'score' in edge_data
        assert 'target' in edge_data