from backend import prepare_sgdbackend, prepare_perfbackend
import conftest
import pytest

def check_reference(reference):
    if reference is not None:
        assert 'link' in reference
        assert 'display_name' in reference
        
def check_reference_extended(reference):
    if reference is not None:
        assert 'display_name' in reference
        assert 'urls' in reference
        assert 'pubmed_id' in reference
        assert 'year' in reference
        assert 'link' in reference
        assert 'id' in reference
        assert 'format_name' in reference
        
        for url in reference['urls']:
            check_url(url)
        
def check_strain(strain):
    if strain is not None:
        assert 'link' in strain
        assert 'display_name' in strain
        assert strain['link'] is None
        
def check_bioent(bioent):
    if bioent is not None:
        assert 'link' in bioent
        assert 'display_name' in bioent
        assert 'format_name' in bioent
        
def check_bioent_extended(bioent):
    if bioent is not None:
        assert 'link' in bioent
        assert 'display_name' in bioent
        assert 'format_name' in bioent
        assert 'dbxref' in bioent
        assert 'id' in bioent
        assert 'bioent_type' in bioent
        
        if bioent['bioent_type'] == 'LOCUS':
            assert 'description' in bioent
        
def check_experiment(experiment):
    if experiment is not None:
        assert 'link' in experiment
        assert 'display_name' in experiment
        assert experiment['link'] is None
    
def check_biocon(biocon):
    if biocon is not None:
        assert 'link' in biocon
        assert 'display_name' in biocon
        
def check_biocon_extended(go):
    if go is not None:
        assert 'link' in go
        assert 'display_name' in go
        assert 'biocon_type' in go
        assert 'format_name' in go
        assert 'id' in go
        
def check_url(url):
    if url is not None:
        assert 'link' in url
        assert 'display_name' in url