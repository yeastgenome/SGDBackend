import json

from src.sgd.backend.tests import check_evidence, check_obj, check_url
from src.sgd.backend.tests.test_basic import check_protein

__author__ = 'kpaskov'

def test_protein_overview_structure(model, identifier='GAL4'):
    response = json.loads(model.protein_overview(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_protein(entry)

def check_protein_domain_evidence(evidence):
    check_evidence(evidence)
    assert 'domain' in evidence
    assert 'protein' in evidence
    assert 'status' in evidence
    assert 'start' in evidence
    assert 'end' in evidence
    assert 'date_of_run' in evidence
    assert 'evalue' in evidence

    check_obj(evidence['domain'])
    check_protein(evidence['protein'])

def test_protein_domain_bioent_details_structure(model, identifier='GAL4'):
    response = json.loads(model.protein_domain_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_protein_domain_evidence(entry)

def test_protein_domain_bioitem_details_structure(model, identifier='PTHR11937'):
    response = json.loads(model.protein_domain_details(domain_identifier=identifier))
    assert response is not None
    for entry in response:
        check_protein_domain_evidence(entry)

def test_protein_domain_graph_structure(model, identifier='GAL4'):
    response = json.loads(model.protein_domain_graph(locus_identifier=identifier))
    assert response is not None
    assert 'max_cutoff' in response
    assert 'nodes' in response
    assert 'edges' in response
    assert 'min_cutoff' in response

    assert len(response['nodes']) < 100
    for node in response['nodes']:
        assert 'data' in node
        assert 'name' in node['data']
        assert 'id' in node['data']
        assert 'link' in node['data']
        assert 'type' in node['data']
        assert 'sub_type' in node['data']

    assert len(response['edges']) < 500
    for edge in response['edges']:
        assert 'data' in edge
        assert 'source' in edge['data']
        assert 'target' in edge['data']
        
def test_binding_site_details_structure(model, identifier='GAL4'):
    response = json.loads(model.binding_site_details(identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'locus' in entry
        assert 'expert_confidence' in entry
        assert 'total_score' in entry
        assert 'motif_id' in entry
        assert 'img_url' in entry
        
        check_obj(entry['locus'])
        assert 'format_name' in entry['locus']

def test_protein_phosphorylation_details_structure(model, identifier='GAL4'):
    response = json.loads(model.protein_phosphorylation_details(identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'protein' in entry
        assert 'site_index' in entry
        assert 'site_residue' in entry

        check_protein(entry['protein'])

def test_protein_resources_structure(model, identifier='YFL039C'):
    response = json.loads(model.protein_resources(locus_identifier=identifier))
    assert response is not None
    assert 'Domain' in response
    assert 'Homologs' in response
    assert 'Other' in response
    assert 'Protein Databases' in response
    assert 'Localization' in response
    for entry in response['Domain']:
        check_url(entry)
    for entry in response['Homologs']:
        check_url(entry)
    for entry in response['Other']:
        check_url(entry)
    for entry in response['Protein Databases']:
        check_url(entry)
    for entry in response['Localization']:
        check_url(entry)