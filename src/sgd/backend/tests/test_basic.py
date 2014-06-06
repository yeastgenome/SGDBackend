import json
import pytest

from src.sgd.backend.tests import check_obj, check_url

__author__ = 'kpaskov'

def test_locus_structure(model, identifier='YFL039C'):
    response = json.loads(model.locus(locus_identifier=identifier))
    assert response is not None
    check_locus(response)

@pytest.mark.xfail()
def test_locus_alias_structure(model, identifier='YFL039C'):
    response = json.loads(model.locus_alias(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_obj(entry)
        assert 'category' in entry
        assert 'source' in entry

def test_locustabs_structure(model, identifier='YFL039C'):
    response = json.loads(model.locustabs(locus_identifier=identifier))
    assert response is not None
    assert 'sequence_tab' in response
    assert 'protein_tab' in response
    assert 'interaction_tab' in response
    assert 'id' in response
    assert 'summary_tab' in response
    assert 'go_tab' in response
    assert 'expression_tab' in response
    assert 'phenotype_tab' in response
    assert 'regulation_tab' in response
    assert 'history_tab' in response
    assert 'literature_tab' in response
    assert 'wiki_tab' in response

def test_bioentity_list_structure(model, bioent_ids=(25, 26, 27, 28, 29)):
    response = json.loads(model.bioentity_list(bioent_ids))
    assert response is not None
    assert len(response) == 5
    for entry in response:
        check_obj(entry)

def test_reference_structure(model, identifier='17112311'):
    response = json.loads(model.reference(reference_identifier=identifier))
    assert response is not None
    check_reference(response)
    assert 'bibentry' in response
    assert 'related_references' in response
    assert 'abstract' in response
    assert 'authors' in response
    assert 'reftypes' in response
    assert 'counts' in response

    assert 'go' in response['counts']
    assert 'regulation' in response['counts']
    assert 'interaction' in response['counts']
    assert 'phenotype' in response['counts']

    for url in response['urls']:
        check_url(url)

    for related_ref in response['related_references']:
        #check_reference(related_ref)
        #Not embedded as a full reference
        assert 'abstract' in related_ref
        assert 'reftypes' in related_ref

    for author in response['authors']:
        check_obj(author)
        assert 'format_name' in author

def test_reference_list_structure(model, reference_ids=None):
    if not reference_ids: reference_ids = [182, 360, 364]
    response = json.loads(model.reference_list(reference_ids))
    assert response is not None
    assert len(response) == 3
    for entry in response:
        assert entry is not None

def test_chemical_structure(model, identifier='benomyl'):
    response = json.loads(model.chemical(chemical_identifier=identifier))
    assert response is not None
    check_obj(response)
    assert 'format_name' in response
    assert 'chebi_id' in response
    assert 'description' in response

def test_author_structure(model, identifier='Bi_E'):
    response = json.loads(model.author(author_identifier=identifier))
    assert response is not None
    check_obj(response)
    assert 'format_name' in response

def test_author_references_structure(model, identifier='Bi_E'):
    response = json.loads(model.author(author_identifier=identifier))
    assert response is not None
    for reference in response['references']:
        check_reference(reference)

def test_new_references_structure(model):
    response = json.loads(model.references_this_week())
    assert response is not None
    assert response['references']
    for reference in response['references']:
        check_reference(reference)

def test_domain_structure(model, identifier='PTHR11937'):
    response = json.loads(model.domain(domain_identifier=identifier))
    assert response is not None
    check_obj(response)
    assert 'interpro_description' in response
    assert 'description' in response
    assert 'source' in response
    assert 'link' in response  ## no longer external_link
    assert 'interpro_id' in response

def test_contig_structure(model, identifier='BY4741_chr08'):
    response = json.loads(model.contig(contig_identifier=identifier))
    assert response is not None
    check_obj(response)
    assert 'residues' in response
    ##assert 'length' in response no longer in object
    assert 'format_name' in response

def check_reference(reference):
    check_obj(reference)
    assert 'pubmed_id' in reference
    assert 'year' in reference
    assert 'journal' in reference
    assert 'citation' in reference
    assert 'format_name' in reference
    assert 'urls' in reference
    for url in reference['urls']:
        check_url(url)

def check_protein(protein):
    check_obj(protein)
    assert 'format_name' in protein
    assert 'locus' in protein
    check_obj(protein['locus'])
    assert 'format_name' in protein['locus']

def check_locus(locus):
    check_obj(locus)
    assert 'sgdid' in locus
    assert 'format_name' in locus
    assert 'description' in locus
    assert 'locus_type' in locus
    #assert 'aliases' in locus  Seems to be empty
    assert 'description' in locus

