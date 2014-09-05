import json

from src.sgd.backend.tests import check_evidence, check_obj

__author__ = 'kpaskov'

def test_sequence_overview_structure(model, identifier='GAL4'):
    response = json.loads(model.locus(locus_identifier=identifier))
    sequence = response['sequence_overview']
    assert sequence is not None
    assert len(sequence) > 20 ## at least 20 strains

def check_sequence_evidence(evidence):
    check_evidence(evidence)
    assert 'residues' in evidence
    assert 'locus' in evidence

    ##check_obj(evidence['residues'])
    check_obj(evidence['locus'])
    assert 'format_name' in evidence['locus']

def check_genomic_sequence_evidence(evidence):
    check_sequence_evidence(evidence)
    assert 'contig' in evidence
    assert 'tags' in evidence
    assert 'strand' in evidence
    assert 'end' in evidence
    assert 'start' in evidence

    check_obj(evidence['contig'])
    assert 'format_name' in evidence['contig']

    for label in evidence['tags']:
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

def test_sequence_contig_details_structure(model, identifier='S288C_Chromosome_12'):
    response = json.loads(model.sequence_details(contig_identifier=identifier))
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