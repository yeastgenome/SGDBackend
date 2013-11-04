'''
Created on Oct 24, 2013

@author: kpaskov
'''

from backend import prepare_sgdbackend, prepare_perfbackend
from model_perf_schema.data import create_data_classes, data_classes
from perfconvert.convert_data import convert_data
from perfconvert_utils import prepare_connections, set_up_logging
import sys

def convert_monthly(perf_dbhost, backend_type, backend_dbhost):
    log = set_up_logging('perfconvert')
    
    session_maker = prepare_connections(perf_dbhost)
    create_data_classes()
    
    log.info('load_backend')
    if backend_type == 'sgdbackend':
        backend = prepare_sgdbackend(DBHOST=backend_dbhost)[0]
    else:
        backend = prepare_perfbackend(DBHOST=backend_dbhost)[0]
    log.info('begin')
    
    ######################### Data ##############################
    
    session = session_maker()
    from model_perf_schema.core import Bioentity
    bioentity_ids = [x.id for x in session.query(Bioentity).all()]
    
    try:
        convert_data(session_maker, data_classes['interaction_overview'], backend.interaction_overview, 'perfconvert.interaction_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['interaction_details'], backend.interaction_details, 'perfconvert.interaction_details', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['interaction_graph'], backend.interaction_graph, 'perfconvert.interaction_graph', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['interaction_resources'], backend.interaction_resources, 'perfconvert.interaction_resources', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        