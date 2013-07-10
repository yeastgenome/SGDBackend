'''
Created on Jul 10, 2013

@author: kpaskov
'''

from datetime import timedelta
from sgdbackend.interaction_views import interaction_overview_table, \
    interaction_evidence_table, interaction_graph
from test import PseudoRequest
import datetime

def test_interaction_overview_table_for_bioent_all(model):
    from query import get_bioent_format_names

    for bioent_format_name in get_bioent_format_names():
        begin_time = datetime.datetime.now()
        response = interaction_overview_table(PseudoRequest(bioent=bioent_format_name))
        end_time = datetime.datetime.now()
        run_time = end_time - begin_time
        assert response is not None
        assert 'aaData' in response
        assert bioent_format_name and run_time < timedelta(seconds=.75)
        
def test_interaction_evidence_table_for_bioent_all(model):
    from query import get_bioent_format_names

    for bioent_format_name in get_bioent_format_names():
        begin_time = datetime.datetime.now()
        response = interaction_evidence_table(PseudoRequest(bioent=bioent_format_name))
        end_time = datetime.datetime.now()
        run_time = end_time - begin_time
        assert response is not None
        assert 'genetic' in response
        assert 'physical' in response
        assert 'reference' in response
        assert bioent_format_name and run_time < timedelta(seconds=.75)
        
def test_interaction_graph_for_bioent_all(model):
    from query import get_bioent_format_names

    for bioent_format_name in get_bioent_format_names():
        begin_time = datetime.datetime.now()
        response = interaction_graph(PseudoRequest(bioent=bioent_format_name))
        end_time = datetime.datetime.now()
        run_time = end_time - begin_time
        assert response is not None
        assert 'dataSchema' in response
        assert 'data' in response
        assert 'nodes' in response['data']
        assert 'edges' in response['data']
        assert 'min_evidence_cutoff' in response
        assert 'max_evidence_cutoff' in response
        assert bioent_format_name and run_time < timedelta(seconds=.75)
        
def test_interaction__evidence_resources_for_bioent_all(model):
    from query import get_bioent_format_names

    for bioent_format_name in get_bioent_format_names():
        begin_time = datetime.datetime.now()
        response = interaction_evidence_resources(PseudoRequest(bioent=bioent_format_name))
        end_time = datetime.datetime.now()
        run_time = end_time - begin_time
        assert response is not None
        assert bioent_format_name and run_time < timedelta(seconds=.75)