import json
import pytest

from src.sgd.backend.tests import check_evidence, check_obj, check_url


__author__ = 'kpaskov'

def test_phenotype_structure(model, identifier='viable'):
    response = json.loads(model.phenotype(identifier))
    assert response is not None
    check_obj(response)
    assert 'description' in response
    assert 'qualifier' in response
    assert 'locus_count' in response
    assert 'observable' in response
    assert 'format_name' in response
    assert 'descendant_locus_count' in response

def test_phenotype_ontology_graph_structure(model, identifier='haploinsufficient'):
    response = json.loads(model.phenotype_ontology_graph(identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
    assert 'all_children' in response
    for node in response['nodes']:
        assert 'data' in node
        assert 'sub_type' in node['data']
        assert 'link' in node['data']
        assert 'id' in node['data']
        assert 'name' in node['data']
    for edge in response['edges']:
        assert 'data' in edge
        assert 'source' in edge['data']
        assert 'target' in edge['data']

def check_phenotype_evidence(evidence):
    check_evidence(evidence)
    assert 'phenotype' in evidence
    assert 'locus' in evidence
    #assert 'conditions' in evidence
    assert 'category' in evidence['experiment']
    assert 'mutant_type' in evidence

    check_obj(evidence['phenotype'])

    check_obj(evidence['locus'])
    assert 'format_name' in evidence['locus']

def test_phenotype_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_biocon_details_structure(model, identifier='cytoskeleton_morphology'):
    response = json.loads(model.phenotype_details(observable_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_biocon_all_details_structure(model, identifier='cytoskeleton_morphology'):
    response = json.loads(model.phenotype_details(observable_identifier=identifier, with_children=True))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_chem_details_structure(model, identifier='benomyl'):
    response = json.loads(model.phenotype_details(chemical_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_graph_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_graph(locus_identifier=identifier))
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