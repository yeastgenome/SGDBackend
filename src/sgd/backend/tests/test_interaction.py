import json
import pytest

from src.sgd.backend.tests import check_url, check_evidence, check_obj

__author__ = 'kpaskov'

def test_interaction_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.locus(locus_identifier=identifier))
    assert response['interaction_overview'] is not None
    ints = response['interaction_overview']
    assert 'gen_circle_size' in ints
    assert 'phys_circle_size' in ints
    assert 'circle_distance' in ints
    assert 'num_gen_interactors' in ints
    assert 'num_phys_interactors' in ints
    assert 'num_both_interactors' in ints

def check_interaction_evidence(evidence):
    #check_evidence(evidence)
    assert 'locus1' in evidence
    assert 'locus2' in evidence
    assert 'bait_hit' in evidence
    assert 'interaction_type' in evidence
    assert 'annotation_type' in evidence

    check_obj(evidence['locus1'])
    assert 'format_name' in evidence['locus1']
    check_obj(evidence['locus2'])
    assert 'format_name' in evidence['locus2']

    if evidence['interaction_type'] == 'Genetic':
        assert 'modification' not in evidence
        assert 'mutant_type' in evidence
        assert 'phenotype' in evidence
        if evidence['phenotype'] is not None:
            check_obj(evidence['phenotype'])
    elif evidence['interaction_type'] == 'Physical':
        assert 'phenotype' not in evidence
        assert 'modification' in evidence
    else:
        assert False

def test_interaction_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_interaction_evidence(entry)

def test_interaction_ref_details_structure(model, identifier='S000057018'):
    response = json.loads(model.interaction_details(reference_identifier=identifier))
    assert response is not None
    for entry in response:
        check_interaction_evidence(entry)

def test_interaction_graph_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_graph(locus_identifier=identifier))
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

@pytest.mark.xfail()   ## not sure if we still have resources or where they are
def test_interaction_resources_structure(model, identifier='YFL039C'):
    response = json.loads(model.interaction_resources(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_url(entry)
