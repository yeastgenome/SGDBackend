from backend import prepare_sgdbackend, prepare_perfbackend
import conftest
import pytest

def check_obj(obj_json):
    if obj_json is not None:
        assert 'id' in obj_json
        assert 'link' in obj_json
        assert 'display_name' in obj_json
        
def check_reference(reference):
    if reference is not None:
        check_obj(reference)

        assert 'urls' in reference
        assert 'pubmed_id' in reference
        assert 'year' in reference
        assert 'format_name' in reference
        
        for url in reference['urls']:
            check_url(url)
        
def check_bioent(bioent):
    if bioent is not None:
        check_obj(bioent)
        assert 'sgdid' in bioent
        assert 'class_type' in bioent
        assert 'format_name' in bioent
        
        if bioent['class_type'] == 'LOCUS':
            assert 'description' in bioent
        
def check_biocon(biocon):
    if biocon is not None:
        check_obj(biocon)
        assert 'biocon_type' in biocon
        assert 'format_name' in biocon
        
def check_url(url):
    if url is not None:
        assert 'link' in url
        assert 'display_name' in url
        
def check_evidence(evidence):
    assert 'id' in evidence
    assert 'class_type' in evidence
    assert 'strain' in evidence
    assert 'source' in evidence
    assert 'reference' in evidence
    assert 'experiment' in evidence
    assert 'note' in evidence
    
    check_obj(evidence['strain'])
    check_obj(evidence['reference'])
    check_obj(evidence['experiment'])
    
def check_condition(condition):
    assert 'note' in condition
    assert 'obj' in condition
    assert 'role' in condition
    check_obj(condition['obj'])
    
    