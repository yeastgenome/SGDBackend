import json

from src.sgd.backend.tests import check_evidence, check_obj, check_url

__author__ = 'kpaskov'

def test_phenotype_structure(model, identifier='cell_cycle_progression_in_G1_phase'):
    response = json.loads(model.phenotype(identifier))
    assert response is not None
    check_obj(response)
    assert 'description' in response
    assert 'ancestor_type' in response
    assert 'is_core' in response
    assert 'qualifier' in response
    assert 'count' in response
    assert 'observable' in response
    assert 'class_type' in response
    assert 'format_name' in response
    assert 'child_count' in response

def test_phenotype_ontology_graph_structure(model, identifier='cell_cycle_progression'):
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

def test_phenotype_ontology_structure(model):
    response = json.loads(model.phenotype_ontology())
    assert response is not None
    assert 'elements' in response
    assert 'child_to_parent' in response
    for element in response['elements']:
        check_obj(element)
        assert 'description' in element
        assert 'ancestor_type' in element
        assert 'is_core' in element
        assert 'qualifier' in element
        assert 'count' in element
        assert 'observable' in element
        assert 'class_type' in element
        assert 'format_name' in element
        assert 'child_count' in element

def test_phenotype_bioent_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_overview(locus_identifier=identifier))
    assert response is not None
    assert 'mutant_types' in response
    assert 'mutant_to_count' in response
    assert 'strain_list' in response
    assert 'strain_to_count' in response
    assert 'experiment_types' in response

def test_phenotype_biocon_overview_structure(model, identifier='heat_sensitivity'):
    response = json.loads(model.phenotype_overview(phenotype_identifier=identifier))
    assert response is not None
    assert 'mutant_types' in response
    assert 'mutant_to_count' in response
    assert 'strain_list' in response
    assert 'strain_to_count' in response
    assert 'experiment_types' in response

def check_phenotype_evidence(evidence):
    check_evidence(evidence)
    assert 'bioconcept' in evidence
    assert 'bioentity' in evidence
    assert 'condition' in evidence
    assert 'experiment_type_category' in evidence
    assert 'chemical' in evidence
    assert 'mutant_type' in evidence
    assert 'reporter' in evidence
    assert 'allele' in evidence

    check_obj(evidence['bioconcept'])
    assert 'description' in evidence['bioconcept']
    assert 'ancestor_type' in evidence['bioconcept']
    assert 'is_core' in evidence['bioconcept']
    assert 'qualifier' in evidence['bioconcept']
    assert 'count' in evidence['bioconcept']
    assert 'observable' in evidence['bioconcept']
    assert 'class_type' in evidence['bioconcept']
    assert 'format_name' in evidence['bioconcept']
    assert 'child_count' in evidence['bioconcept']

    check_obj(evidence['bioentity'])
    assert 'format_name' in evidence['bioentity']
    assert 'class_type' in evidence['bioentity']

    if evidence['allele'] is not None:
        check_obj(evidence['allele'])
        assert 'note' in evidence['allele']

    if evidence['chemical'] is not None:
        check_obj(evidence['chemical'])
        assert 'note' in evidence['chemical']

    if evidence['reporter'] is not None:
        check_obj(evidence['reporter'])
        assert 'note' in evidence['reporter']

def test_phenotype_bioent_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_biocon_details_structure(model, identifier='cytoskeleton_morphology'):
    response = json.loads(model.phenotype_details(phenotype_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_biocon_all_details_structure(model, identifier='cytoskeleton_morphology'):
    response = json.loads(model.phenotype_details(phenotype_identifier=identifier, with_children=True))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_ref_details_structure(model, identifier='S000055780'):
    response = json.loads(model.phenotype_details(reference_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

def test_phenotype_chem_details_structure(model, identifier='benomyl'):
    response = json.loads(model.phenotype_details(chemical_identifier=identifier))
    assert response is not None
    for entry in response:
        check_phenotype_evidence(entry)

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