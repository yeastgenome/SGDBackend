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
    from model_perf_schema.core import Bioentity, Bioconcept
    bioentity_ids = [x.id for x in session.query(Bioentity).all()]
    bioconcept_ids = [x.id for x in session.query(Bioconcept).all()]
    
    try:
        convert_data(session_maker, data_classes['interaction_overview'], backend.interaction_overview, 'perfconvert.interaction_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['interaction_details'], backend.interaction_details, 'perfconvert.interaction_details', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['interaction_graph'], backend.interaction_graph, 'perfconvert.interaction_graph', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['interaction_resources'], backend.interaction_resources, 'perfconvert.interaction_resources', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        