'''
Created on Jul 10, 2013

@author: kpaskov
'''

from sgdbackend.cache import id_to_bioent
from sgdbackend.interaction_views import interaction_graph, interaction_overview, \
    interaction_details, interaction_resources, interaction_references
from sgdbackend_test import PseudoRequest, model
import pytest

slow = pytest.mark.slow

def test_interaction_overview_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = interaction_overview(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
    assert 'gen_circle_size' in response
    assert 'phys_circle_size' in response
    assert 'circle_distance' in response
    assert 'num_gen_interactors' in response
    assert 'num_phys_interactors' in response
    assert 'num_both_interactors' in response
    
@slow
def test_interaction_overview_all(model):
    for bioent in id_to_bioent.values():
        test_interaction_overview_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])
        
def test_interaction_details_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = interaction_details(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
     
@slow   
def test_interaction_details_all(model):
    for bioent in id_to_bioent.values():
        test_interaction_details_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])
 
def test_interaction_graph_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = interaction_graph(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
    assert 'min_evidence_cutoff' in response
    assert 'max_evidence_cutoff' in response
    assert 'max_phys_cutoff' in response
    assert 'max_gen_cutoff' in response
    assert 'max_both_cutoff' in response
     
@slow   
def test_interaction_graph_all(model):
    for bioent in id_to_bioent.values():
        test_interaction_details_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])

def test_interaction_resources_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = interaction_resources(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
    assert len(response) > 0
    
@slow    
def test_interaction_resources_all(model):
    for bioent in id_to_bioent.values():
        test_interaction_details_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])
    
def test_interaction_references_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = interaction_references(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None

@slow
def test_interaction_references_all(model):
    for bioent in id_to_bioent.values():
        test_interaction_details_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])

