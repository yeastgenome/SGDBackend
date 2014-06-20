import json
import pytest

from src.sgd.backend.tests import check_evidence, check_obj, check_url


__author__ = 'kpaskov'

def test_phenotype_structure(model, identifier='viable'):
    response = json.loads(model.phenotype(identifier))
    assert response is not None
    check_obj(response)
    # I think some of these were moved to graph
    assert 'description' in response
    #assert 'ancestor_type' in response
    #assert 'is_core' in response
    assert 'qualifier' in response
    #assert 'count' in response
    assert 'observable' in response
    assert 'format_name' in response
    #assert 'child_count' in response

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

@pytest.mark.xfail() # No longer valid
def test_phenotype_ontology_structure(model):
    response = json.loads(model.phenotype_ontology())
    assert response is not None
    assert 'elements' in response
    assert 'child_to_parent' in response
    for element in response['elements']:
        check_obj(element)

def test_phenotype_bioent_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.locus(locus_identifier=identifier))
    assert response is not None
    phenotypes = response['phenotype_overview']
    # why is this not a hash/dict?
    assert phenotypes['experiment_categories'][0] == [u'Mutant Type', u'classical genetics', u'large-scale survey']
    assert phenotypes['strains'][0] == [u'Strain', u'Annotations']
    #assert 'mutant_types' in phenotypes
    #assert 'mutant_to_count' in phenotypes
    #assert 'strain_list' in phenotypes
    #assert 'strain_to_count' in phenotypes
    #assert 'experiment_types' in phenotypes

@pytest.mark.xfail()  # no idea what this is supposed to test
def test_phenotype_biocon_overview_structure(model, identifier='viable'):
    response = json.loads(model.phenotype(phenotype_identifier=identifier))
    assert response is not None
    phenotypes = response['phenotype_overview']
    assert 'mutant_types' in phenotypes
    assert 'mutant_to_count' in phenotypes
    assert 'strain_list' in phenotypes
    assert 'strain_to_count' in phenotypes
    assert 'experiment_types' in phenotypes

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

@pytest.mark.xfail()  ## phenotype_details not really used any longer.
def test_phenotype_biocon_details_structure(model, identifier='cytoskeleton_morphology'):
    response = json.loads(model.phenotype_details(phenotype_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

@pytest.mark.xfail()  ## phenotype_details not really used any longer.
def test_phenotype_biocon_all_details_structure(model, identifier='cytoskeleton_morphology'):
    response = json.loads(model.phenotype_details(phenotype_identifier=identifier, with_children=True))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

@pytest.mark.xfail()  ## phenotype_details not really used any longer.
def test_phenotype_ref_details_structure(model, identifier='S000055780'):
    response = json.loads(model.phenotype_details(reference_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

@pytest.mark.xfail()  ## phenotype_details not really used any longer.
def test_phenotype_chem_details_structure(model, identifier='benomyl'):
    response = json.loads(model.phenotype_details(chemical_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

@pytest.mark.xfail()  ## phenotype_resources not really used any longer.
def test_phenotype_resources_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_resources(locus_identifier=identifier))
    assert response is not None
    assert 'Phenotype Resources' in response
    assert 'Mutant Resources' in response
    for entry in response['Phenotype Resources']:
        check_url(entry)
    for entry in response['Mutant Resources']:
        check_url(entry)

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