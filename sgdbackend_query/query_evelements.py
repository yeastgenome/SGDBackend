'''
Created on Oct 26, 2013

@author: kpaskov
'''
from model_new_schema.evelements import Experimentrelation
from sgdbackend_query import session

#Used for ontology graphs
def get_experiment_graph(print_query=False):
    child_to_parent_id = {}
    query = session.query(Experimentrelation)

    if print_query:
        print query

    return dict([(x.child_id, x.parent_id) for x in query.all()])