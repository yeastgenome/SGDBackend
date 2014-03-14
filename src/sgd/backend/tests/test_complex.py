import json

from src.sgd.backend.tests import check_obj
from src.sgd.backend.tests.test_go import check_go_evidence

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
    assert 'class_type' in response['go']

def test_complex_genes_structure(model, identifier='TRAPP_complex'):
    response = json.loads(model.complex_genes(complex_identifier=identifier))
    assert response is not None
    for gene in response:
        check_obj(gene)
        assert 'locus_type' in gene
        assert 'class_type' in gene
        assert 'sgdid' in gene
        assert 'aliases' in gene
        assert 'description' in gene

def test_complex_details_structure(model, identifier='TRAPP_complex'):
    response = json.loads(model.complex_details(complex_identifier=identifier))
    assert response is not None
    for entry in response:
        check_go_evidence(entry)

def test_complex_graph(model, identifier='TRAPP_complex'):
    response = json.loads(model.complex_graph(complex_identifier=identifier))
    assert response is not None
    assert 'max_cutoff' in response
    assert 'nodes' in response
    assert 'edges' in response
    assert 'min_cutoff' in response

    assert len(response['nodes']) < 100
    for node in response['nodes']:
        assert 'data' in node
        assert 'name' in node['data']
        assert 'gene_count' in node['data']
        assert 'id' in node['data']
        assert 'link' in node['data']
        assert 'type' in node['data']
        assert 'sub_type' in node['data']

    assert len(response['edges']) < 500
    for edge in response['edges']:
        assert 'data' in edge
        assert 'source' in edge['data']
        assert 'target' in edge['data']


    

