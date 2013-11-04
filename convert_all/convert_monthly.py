'''
Created on Oct 24, 2013

@author: kpaskov
'''

from convert_core import convert_reference, convert_bioentity, \
    convert_evelements, convert_chemical, convert_bioconcept, convert_bioitem
from convert_evidence import convert_interaction
from convert_utils import set_up_logging, prepare_connections
import sys

if __name__ == "__main__":   
    old_session_maker, new_session_maker = prepare_connections()
    
    log = set_up_logging('convert')
    log.info('begin')
    
    ######################### Core ##############################
    #Evelement
    try:
        convert_evelements.convert(old_session_maker, new_session_maker)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    #Reference
    try:
        convert_reference.convert(old_session_maker, new_session_maker)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Bioentity
    try:
        convert_bioentity.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Bioconcept
    try:
        convert_bioconcept.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Bioitem
    try:
        convert_bioitem.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Chemical
    try:
        convert_chemical.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    ######################### Evidence ##############################
     
    #Interaction
    try:
        convert_interaction.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    from perfconvert.convert_monthly import convert_monthly
    #Converts nex->perf on sgd-db2
    convert_monthly('sgd-db2.stanford.edu:1521', 'sgdbackend', 'sgd-db2.stanford.edu:1521')
    
    #Converts perf on sgd-db2 -> perf on sgd-db1
    #convert_monthly('sgd-db1.stanford.edu:1521', 'perfbackend', 'sgd-db2.stanford.edu:1521')
        
    