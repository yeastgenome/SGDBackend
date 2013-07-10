'''
Created on Jul 10, 2013

@author: kpaskov
'''

from datetime import timedelta
from sgdbackend import prep_sqlalchemy, prep_views
from sgdbackend.interaction_views import interaction_overview_table, \
    interaction_evidence_table, interaction_graph, interaction_evidence_resources
from test import PseudoRequest
import datetime
import pytest

@pytest.fixture(scope="module")
def model():
    config = prep_sqlalchemy()
    prep_views(config)

def test_interaction_overview_table_for_bioent_structure(model):
    response = interaction_overview_table(PseudoRequest(bioent='YFL039C'))
    assert response is not None
    assert 'aaData' in response
    
def test_interaction_overview_table_for_bioent_speed(model):
    begin_time = datetime.datetime.now()
    interaction_overview_table(PseudoRequest(bioent='YFL039C'))
    end_time = datetime.datetime.now()
    assert end_time - begin_time < timedelta(seconds=.2)
        
def test_interaction_evidence_table_for_bioent_structure(model):
    response = interaction_evidence_table(PseudoRequest(bioent='YFL039C'))
    assert response is not None
    assert 'genetic' in response
    assert 'physical' in response
    assert 'reference' in response
    
def test_interaction_evidence_table_for_bioent_speed(model):
    begin_time = datetime.datetime.now()
    interaction_evidence_table(PseudoRequest(bioent='YFL039C'))
    end_time = datetime.datetime.now()
    assert end_time - begin_time < timedelta(seconds=.2)
        
def test_interaction_graph_for_bioent_structure(model):
    response = interaction_graph(PseudoRequest(bioent='YFL039C'))
    assert response is not None
    assert 'dataSchema' in response
    assert 'data' in response
    assert 'nodes' in response['data']
    assert 'edges' in response['data']
    assert 'min_evidence_cutoff' in response
    assert 'max_evidence_cutoff' in response
    
def test_interaction_graph_for_bioent_speed(model):
    begin_time = datetime.datetime.now()
    interaction_graph(PseudoRequest(bioent='YFL039C'))
    end_time = datetime.datetime.now()
    assert end_time - begin_time < timedelta(seconds=.2)
        
def test_interaction_evidence_resources_for_bioent_structure(model):
    response = interaction_evidence_resources(PseudoRequest(bioent='YFL039C'))
    assert response is not None
    
def test_interaction__evidence_resources_for_bioent_speed(model):
    begin_time = datetime.datetime.now()
    interaction_evidence_resources(PseudoRequest(bioent='YFL039C'))
    end_time = datetime.datetime.now()
    assert end_time - begin_time < timedelta(seconds=.2)
    
#def test_interaction_overview_table_for_ref_structure(model):
#    response = interaction_overview_table(PseudoRequest(reference='2656402'))
#    print response
#    assert response is not None
#    assert 'aaData' in response

