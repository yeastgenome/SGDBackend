'''
Created on Jul 10, 2013

@author: kpaskov
'''

from sgdbackend.cache import id_to_bioent
from sgdbackend.literature_views import literature_overview, literature_details, \
    literature_graph
from sgdbackend_test import PseudoRequest, model
import pytest

slow = pytest.mark.slow

def test_literature_overview_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = literature_overview(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
    assert len(response) > 0
    
@slow
def test_literature_overview_all(model):
    for bioent in id_to_bioent.values():
        test_literature_overview_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])
        
def test_literature_details_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = literature_details(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
    assert 'primary' in response
    assert 'additional' in response
    assert 'reviews' in response
     
@slow   
def test_literature_details_all(model):
    for bioent in id_to_bioent.values():
        test_literature_details_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])
 
def test_literature_graph_structure(model, bioent_type='LOCUS', identifier='YFL039C'):
    response = literature_graph(PseudoRequest(type=bioent_type, identifier=identifier))
    assert response is not None
    assert 'nodes' in response
    assert 'edges' in response
     
@slow   
def test_literature_graph_all(model):
    for bioent in id_to_bioent.values():
        test_literature_graph_structure(model, bioent_type=bioent['bioent_type'], identifier=bioent['format_name'])
    