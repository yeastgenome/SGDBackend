import json

from src.sgd.backend.tests import check_evidence, check_obj
from src.sgd.backend.tests.test_basic import check_reference

__author__ = 'kpaskov'

def test_regulation_overview_structure(model, identifier='GAL4'):
    response = json.loads(model.locus(locus_identifier=identifier))
    regulation = response['regulation_overview']
    assert regulation is not None
    assert 'regulator_count' in regulation
    assert 'target_count' in regulation

def test_regulation_paragraph_structure(model, identifier='GAL4'):
    response = json.loads(model.locus(locus_identifier=identifier))
    paragraph = response['regulation_overview']['paragraph']
    if paragraph is not None:
        assert 'text' in paragraph
        assert 'references' in paragraph
        for reference in paragraph['references']:
            check_reference(reference)

def check_regulation_evidence(evidence):
    check_evidence(evidence)
    assert 'locus1' in evidence
    assert 'locus2' in evidence
    #assert 'conditions' in evidence

    check_obj(evidence['locus1'])
    assert 'format_name' in evidence['locus1']
    check_obj(evidence['locus2'])
    assert 'format_name' in evidence['locus2']

def test_regulation_bioent_details_structure(model, identifier='GAL4'):
    response = json.loads(model.regulation_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_regulation_evidence(entry)

def test_regulation_ref_details_structure(model, identifier='16449570'):
    response = json.loads(model.regulation_details(reference_identifier=identifier))
    assert response is not None
    for entry in response:
        check_regulation_evidence(entry)

def test_regulation_graph_structure(model, identifier='GAL4'):
    response = json.loads(model.regulation_graph(locus_identifier=identifier))
    assert response is not None
    assert 'edges' in response
    assert 'nodes' in response

    assert len(response['nodes']) < 100
    for entry in response['edges']:
        assert 'data' in entry
        edge_data = entry['data']
        assert 'source' in edge_data
        assert 'target' in edge_data
        assert 'evidence' in edge_data

    assert len(response['edges']) < 500
    for entry in response['nodes']:
        assert 'data' in entry
        node_data = entry['data']
        assert 'link' in node_data
        assert 'id' in node_data
        assert 'sub_type' in node_data
        assert 'name' in node_data

def test_regulation_target_enrichment_structure(model, identifier='ADF1'):
    response = json.loads(model.regulation_target_enrichment(locus_identifier=identifier))
    assert response is not None

    for entry in response:
        assert 'go' in entry
        assert 'match_count' in entry
        assert 'pvalue' in entry
        check_obj(entry['go'])
        assert 'format_name' in entry['go']
        assert 'go_id' in entry['go']
        assert 'go_aspect' in entry['go']