import json

from src.sgd.backend.tests import check_evidence, check_obj

__author__ = 'kpaskov'

def test_sequence_overview_structure(model, identifier='GAL4'):
    response = json.loads(model.sequence_overview(locus_identifier=identifier))
    assert response is not None

def check_sequence_evidence(evidence):
    check_evidence(evidence)
    assert 'sequence' in evidence
    assert 'bioentity' in evidence

    check_obj(evidence['sequence'])
    check_obj(evidence['bioentity'])
    assert 'format_name' in evidence['bioentity']
    assert 'class_type' in evidence['bioentity']

def check_genomic_sequence_evidence(evidence):
    check_sequence_evidence(evidence)
    assert 'neighbors' in evidence
    assert 'contig' in evidence
    assert 'sequence_labels' in evidence
    assert 'strand' in evidence
    assert 'end' in evidence
    assert 'start' in evidence

    for neighbor in evidence['neighbors']:
        assert 'start' in neighbor
        assert 'end' in neighbor
        assert 'strand' in neighbor
        assert 'display_name' in neighbor

    check_obj(evidence['contig'])
    assert 'residues' in evidence['contig']
    assert 'length' in evidence['contig']
    assert 'format_name' in evidence['contig']

    for label in evidence['sequence_labels']:
        assert 'chromosomal_start' in label
        assert 'relative_start' in label
        assert 'relative_end' in label
        assert 'display_name' in label
        assert 'chromosomal_end' in label

def test_sequence_bioent_details_structure(model, identifier='GAL4'):
    response = json.loads(model.sequence_details(locus_identifier=identifier))
    assert response is not None
    assert 'protein' in response
    assert 'coding_dna' in response
    assert 'genomic_dna' in response

    for entry in response['protein']:
        check_sequence_evidence(entry)
    for entry in response['coding_dna']:
        check_sequence_evidence(entry)
    for entry in response['genomic_dna']:
        check_genomic_sequence_evidence(entry)

def test_sequence_contig_details_structure(model, identifier='BY4741_chr08'):
    response = json.loads(model.sequence_details(contig_identifier=identifier))
    assert response is not None
    for entry in response:
        check_sequence_evidence(entry)