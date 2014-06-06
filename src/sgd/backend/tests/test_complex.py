import json

from src.sgd.backend.tests import check_obj, check_evidence

__author__ = 'kpaskov'

def test_complex_structure(model, identifier='TRAPP_complex'):
    response = json.loads(model.complex(complex_identifier=identifier))
    assert response is not None
    check_obj(response)
    assert 'class_type' in response
    assert 'go' in response
    assert 'cellular_localization' in response
    assert 'sgdid' in response
    assert 'description' in response
    check_obj(response['go'])

def test_complex_details_structure(model, identifier='TRAPP_complex'):
    response = json.loads(model.complex_details(complex_identifier=identifier))
    assert response is not None
    for evidence in response:
        check_complex_evidence(evidence)

def check_complex_evidence(evidence):
    check_evidence(evidence)
    assert 'locus' in evidence
    assert 'go' in evidence
    assert 'complex' in evidence

    check_obj(evidence['go'])
    assert 'go_id' in evidence['go']
    assert 'aspect' in evidence['go']

    check_obj(evidence['locus'])
    assert 'format_name' in evidence['locus']

    check_obj(evidence['complex'])
    assert 'format_name' in evidence['complex']

def test_complex_graph(model, identifier='TRAPP_complex'):
    response = json.loads(model.complex_graph(complex_identifier=identifier))
    assert response is not None
    assert 'go_graph' in response
    assert 'interaction_graph' in response
    ## these pass but these graphs are currently empty
    for key, graph in response.items():
        #assert graph['max_cutoff'] == 0  MISSING from go_graph
        assert 'nodes' in graph
        assert 'edges' in graph
        #assert graph['min_cutoff'] == 0  MISSING from go_graph

        assert len(graph['nodes']) < 100
        for node in graph['nodes']:
            assert 'data' in node
            assert 'name' in node['data']
            assert 'gene_count' in node['data']
            assert 'id' in node['data']
            assert 'link' in node['data']
            assert 'type' in node['data']
            assert 'sub_type' in node['data']

        assert len(graph['edges']) < 500
        for edge in graph['edges']:
            assert 'data' in edge
            assert 'source' in edge['data']
            assert 'target' in edge['data']




