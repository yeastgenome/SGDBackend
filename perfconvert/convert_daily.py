'''
Created on Oct 24, 2013

@author: kpaskov
'''

from backend import prepare_sgdbackend
from model_perf_schema.data import create_data_classes, data_classes
from perfconvert import convert_core
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
    
    ######################### Core ##############################
#    #Disambigs
#    try:
#        convert_core.convert_disambig(session_maker, backend, 10000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#        
#    #Bioentity
#    try:
#        convert_core.convert_bioentity(session_maker, backend, 1000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
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
        
    ######################### Data ##############################
    
    session = session_maker()
    from model_perf_schema.core import Bioentity, Bioconcept
    bioentity_ids = [x.id for x in session.query(Bioentity).all()]
    bioconcept_ids = [x.id for x in session.query(Bioconcept).all()]
        
    try:
        convert_data(session_maker, data_classes['literature_overview'], backend.literature_overview, 'perfconvert.literature_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['literature_details'], backend.literature_details, 'perfconvert.literature_details', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['literature_graph'], backend.literature_graph, 'perfconvert.literature_graph', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    try:
        convert_data(session_maker, data_classes['go_overview'], backend.go_overview, 'perfconvert.go_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['go_ontology_graph'], backend.go_ontology_graph, 'perfconvert.go_ontology_graph', bioconcept_ids, 1000)
        convert_data(session_maker, data_classes['go_details_bioent'], backend.go_details_bioent, 'perfconvert.go_details_bioent', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['go_details_biocon'], backend.go_details_biocon, 'perfconvert.go_details_biocon', bioconcept_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    try:
        convert_data(session_maker, data_classes['phenotype_overview'], backend.phenotype_overview, 'perfconvert.phenotype_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['phenotype_ontology_graph'], backend.phenotype_ontology_graph, 'perfconvert.phenotype_ontology_graph', bioconcept_ids, 1000)
        convert_data(session_maker, data_classes['phenotype_details_bioent'], backend.phenotype_details_bioent, 'perfconvert.phenotype_details_bioent', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['phenotype_details_biocon'], backend.phenotype_details_biocon, 'perfconvert.phenotype_details_biocon', bioconcept_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        