import json

from src.sgd.backend.tests import check_evidence, check_obj, check_condition

__author__ = 'kpaskov'

def test_go_structure(model, identifier='GO:0018706'):
    response = json.loads(model.go(go_identifier=identifier))
    assert response is not None
    check_obj(response)
    assert 'description' in response
    assert 'aliases' in response
    assert 'count' in response
    assert 'class_type' in response
    assert 'format_name' in response
    assert 'go_id' in response
    assert 'child_count' in response
    assert 'go_aspect' in response

def test_go_ontology_graph_structure(model, identifier='GO:0018706'):
    response = json.loads(model.go_ontology_graph(go_identifier=identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
    assert 'all_children' in response
    for node in response['nodes']:
        assert node is not None
        assert 'data' in node
        assert node['data'] is not None
        assert 'sub_type' in node['data']
        assert 'link' in node['data']
        assert 'id' in node['data']
        assert 'name' in node['data']
    for edge in response['edges']:
        assert edge is not None
        assert 'data' in edge
        assert edge['data'] is not None
        assert 'source' in edge['data']
        assert 'target' in edge['data']
        assert 'name' in edge['data']

def test_go_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.go_overview(locus_identifier=identifier))
    assert response is not None
    assert 'go_slim' in response
    assert 'date_last_reviewed' in response
    for entry in response['go_slim']:
        check_obj(entry)
        assert 'class_type' in entry

def check_go_evidence(evidence):
    check_evidence(evidence)
    assert 'bioconcept' in evidence
    assert 'bioentity' in evidence
    assert 'conditions' in evidence
    assert 'qualifier' in evidence
    assert 'code' in evidence
    assert 'date_created' in evidence
    assert 'method' in evidence

    check_obj(evidence['bioconcept'])
    assert 'class_type' in evidence['bioconcept']
    assert 'go_id' in evidence['bioconcept']
    assert 'aspect' in evidence['bioconcept']

    check_obj(evidence['bioentity'])
    assert 'format_name' in evidence['bioentity']
    assert 'class_type' in evidence['bioentity']

    for cond in evidence['conditions']:
        check_condition(cond)

def test_go_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.go_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_go_evidence(entry)

def test_go_biocon_details_structure(model, identifier='GO:0000916'):
    response = json.loads(model.go_details(go_identifier=identifier))
    assert response is not None
    for entry in response:
        check_go_evidence(entry)

def test_go_biocon_all_details_structure(model, identifier='GO:0000916'):
    response = json.loads(model.go_details(go_identifier=identifier, with_children=True))
    assert response is not None
    for entry in response:
        check_go_evidence(entry)

def test_go_ref_details_structure(model, identifier='S000053564'):
    response = json.loads(model.go_details(reference_identifier=identifier))
    assert response is not None
    for entry in response:
        check_go_evidence(entry)

def test_go_enrichment_structure(model, bioent_ids=None):
    if not bioent_ids: bioent_ids = [3485, 5783, 4131, 3306, 4258, 6159, 2615, 5609, 1633, 6917]
    response = json.loads(model.go_enrichment(bioent_ids))
    assert response is not None

def test_go_graph(model, identifier='YFL039C'):
    response = json.loads(model.go_graph(locus_identifier=identifier))
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
    

    

