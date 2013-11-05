'''
Created on Oct 24, 2013

@author: kpaskov
'''

from model_perf_schema.data import create_data_classes, data_classes
from perfbackend import prepare_perfbackend
from perfconvert.convert_data import convert_data
from perfconvert_utils import prepare_connections, set_up_logging
from sgdbackend import prepare_sgdbackend
import sys

def convert_updated_flatfiles(perf_dbhost, backend_type, backend_dbhost):
    log = set_up_logging('perfconvert')
    
    session_maker = prepare_connections(perf_dbhost)
    create_data_classes()
    
    log.info('load_backend')
    if backend_type == 'sgdbackend':
        backend = prepare_sgdbackend(DBHOST=backend_dbhost)
    else:
        backend = prepare_perfbackend(DBHOST=backend_dbhost)
    log.info('begin')
        
    ######################### Data ##############################
    
    session = session_maker()
    from model_perf_schema.core import Bioentity
    bioentity_ids = [x.id for x in session.query(Bioentity).all()]
    
    try:
        convert_data(session_maker, data_classes['regulation_overview'], backend.regulation_overview, 'perfconvert.regulation_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['regulation_details'], backend.regulation_details, 'perfconvert.regulation_details', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['regulation_graph'], backend.regulation_graph, 'perfconvert.regulation_graph', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['regulation_target_enrich'], backend.regulation_target_enrichment, 'perfconvert.regulation_target_enrichment', bioentity_ids, 100)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    try:
        convert_data(session_maker, data_classes['protein_domain_details'], backend.protein_domain_details, 'perfconvert.protein_domain_details', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    try:
        convert_data(session_maker, data_classes['binding_site_details'], backend.binding_site_details, 'perfconvert.binding_site_details', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )