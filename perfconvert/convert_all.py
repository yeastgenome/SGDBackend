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
    
    ######################## Core ##############################
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
#    
#    #Bioconcept
#    try:
#        convert_core.convert_bioconcept(session_maker, backend, 10000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
#    
#    #Reference
#    try:
#        convert_core.convert_reference(session_maker, backend, 1000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    ######################### Data ##############################
    
    session = session_maker()
    from model_perf_schema.core import Bioentity, Bioconcept
    bioentity_ids = [x.id for x in session.query(Bioentity).all()]
    bioconcept_ids = [x.id for x in session.query(Bioconcept).all()]
    
#    #Interaction
#    try:
#        convert_data(session_maker, data_classes['interaction_overview'], backend.interaction_overview, 'perfconvert.interaction_overview', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['interaction_details'], backend.interaction_details, 'perfconvert.interaction_details', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['interaction_graph'], backend.interaction_graph, 'perfconvert.interaction_graph', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['interaction_resources'], backend.interaction_resources, 'perfconvert.interaction_resources', bioentity_ids, 1000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
#    #Literature    
#    try:
#        convert_data(session_maker, data_classes['literature_overview'], backend.literature_overview, 'perfconvert.literature_overview', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['literature_details'], backend.literature_details, 'perfconvert.literature_details', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['literature_graph'], backend.literature_graph, 'perfconvert.literature_graph', bioentity_ids, 1000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #GO    
    try:
        #convert_data(session_maker, data_classes['go_overview'], backend.go_overview, 'perfconvert.go_overview', bioentity_ids, 1000)
        #convert_data(session_maker, data_classes['go_ontology_graph'], backend.go_ontology_graph, 'perfconvert.go_ontology_graph', bioconcept_ids, 1000)
        convert_data(session_maker, data_classes['go_details_bioent'], lambda x: backend.go_details(locus_identifier=x), 'perfconvert.go_details_bioent', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['go_details_biocon'], lambda x: backend.go_details(go_identifier=x), 'perfconvert.go_details_biocon', bioconcept_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Phenotype    
    try:
        #convert_data(session_maker, data_classes['phenotype_overview'], backend.phenotype_overview, 'perfconvert.phenotype_overview', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['phenotype_ontology_graph'], backend.phenotype_ontology_graph, 'perfconvert.phenotype_ontology_graph', bioconcept_ids, 1000)
        convert_data(session_maker, data_classes['phenotype_details_bioent'], lambda x: backend.phenotype_details(locus_identifier=x), 'perfconvert.phenotype_details_bioent', bioentity_ids, 1000)
        convert_data(session_maker, data_classes['phenotype_details_biocon'], lambda x: backend.phenotype_details(phenotype_identifier=x), 'perfconvert.phenotype_details_biocon', bioconcept_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Protein domain details    
    try:
        convert_data(session_maker, data_classes['protein_domain_details'], backend.protein_domain_details, 'perfconvert.protein_domain_details', bioentity_ids, 1000)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
#    #Binding site details   
#    try:
#        convert_data(session_maker, data_classes['binding_site_details'], backend.binding_site_details, 'perfconvert.binding_site_details', bioentity_ids, 1000)
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )

#    #Regulation    
#    try:
#        #Problem here V
#        convert_data(session_maker, data_classes['regulation_overview'], backend.regulation_overview, 'perfconvert.regulation_overview', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['regulation_details'], backend.regulation_details, 'perfconvert.regulation_details', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['regulation_graph'], backend.regulation_graph, 'perfconvert.regulation_graph', bioentity_ids, 1000)
#        convert_data(session_maker, data_classes['regulation_target_enrich'], backend.regulation_target_enrichment, 'perfconvert.regulation_target_enrichment', bioentity_ids, 100)
#
#    except Exception:
#        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
        