import json

from src.sgd.backend.tests import check_evidence, check_obj
from src.sgd.backend.tests.test_basic import check_reference


__author__ = 'kpaskov'

def test_literature_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.locus(locus_identifier=identifier))
    literature = response['literature_overview']
    assert 'total_count' in literature

def test_literature_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.literature_details(locus_identifier=identifier))
    assert response is not None
    assert 'primary' in response
    assert 'additional' in response
    assert 'review' in response
    assert 'phenotype' in response
    assert 'go' in response
    assert 'interaction' in response
    assert 'regulation' in response

    for entry in response['primary']:
        check_reference(entry)
    for entry in response['additional']:
        check_reference(entry)
    for entry in response['review']:
        check_reference(entry)
    for entry in response['phenotype']:
        check_reference(entry)
    for entry in response['go']:
        check_reference(entry)
    for entry in response['interaction']:
        check_reference(entry)
    for entry in response['regulation']:
        check_reference(entry)

def test_literature_graph_structure(model, identifier='YFL039C'):
    response = json.loads(model.literature_graph(locus_identifier=identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response

    assert len(response['nodes']) < 100
    for node_entry in response['nodes']:
        assert 'data' in node_entry
        node_data = node_entry['data']
        assert 'type' in node_data
        assert 'sub_type' in node_data
        assert 'link' in node_data
        assert 'id' in node_data
        assert 'name' in node_data

    assert len(response['edges']) < 500
    for edge_entry in response['edges']:
        assert 'data' in edge_entry
        edge_data = edge_entry['data']
        assert 'source' in edge_data
        assert 'target' in edge_data