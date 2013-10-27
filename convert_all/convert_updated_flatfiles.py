'''
Created on Oct 24, 2013

@author: kpaskov
'''

from convert_core import convert_reference, convert_bioentity, \
    convert_evelements, convert_chemical, convert_bioconcept, convert_bioitem
from convert_evidence import convert_binding, \
    convert_protein, convert_regulation
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
     
    #Binding
    try:
        convert_binding.convert(new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Protein
    try:
        convert_protein.convert(new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Regulation
    try:
        convert_regulation.convert(new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    