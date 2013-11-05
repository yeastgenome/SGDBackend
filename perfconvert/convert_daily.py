'''
Created on Oct 24, 2013

@author: kpaskov
'''

from model_perf_schema.data import create_data_classes, data_classes
from perfbackend import prepare_perfbackend
from perfconvert import convert_core
from perfconvert.convert_data import convert_data
from perfconvert_utils import prepare_connections, set_up_logging
from sgdbackend import prepare_sgdbackend
import sys

def convert_daily(perf_dbhost, backend_type, backend_dbhost):
    log = set_up_logging('perfconvert')
    
    session_maker = prepare_connections(perf_dbhost)
    create_data_classes()
    
    log.info('load_backend')
    if backend_type == 'sgdbackend':
        backend = prepare_sgdbackend(DBHOST=backend_dbhost)
    else:
        backend = prepare_perfbackend(DBHOST=backend_dbhost)
    log.info('begin')
    
    ######################### Core ##############################
    #Bioentity
    try:
        convert_core.convert_bioentity(session_maker, backend, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Bioconcept
    try:
        convert_core.convert_bioconcept(session_maker, backend, 10000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Reference
    try:
        convert_core.convert_reference(session_maker, backend, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Disambigs
    try:
        convert_core.convert_disambig(session_maker, backend, 10000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    ######################### Data ##############################
    
    session = session_maker()
    from model_perf_schema.core import Bioentity
    bioentity_ids = [x.id for x in session.query(Bioentity).all()]
        
    try:
        convert_data(session_maker, data_classes['literature_overview'], backend.literature_overview, 'perfconvert.literature_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['literature_details'], backend.literature_details, 'perfconvert.literature_details', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['literature_graph'], backend.literature_graph, 'perfconvert.literature_graph', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        