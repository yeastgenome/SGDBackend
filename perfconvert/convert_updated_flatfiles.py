'''
Created on Oct 24, 2013

@author: kpaskov
'''

from backend import prepare_sgdbackend
from model_perf_schema.data import create_data_classes, data_classes
from perfconvert.convert_data import convert_data
from perfconvert_utils import prepare_connections, set_up_logging
import sys

if __name__ == "__main__":   
    log = set_up_logging('perfconvert')
    
    session_maker = prepare_connections()
    create_data_classes()
    
    log.info('load_sgdbackend')
    backend = prepare_sgdbackend()[0]
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