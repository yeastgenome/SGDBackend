'''
Created on Oct 24, 2013

@author: kpaskov
'''

from convert_core import convert_reference, convert_bioentity, \
    convert_evelements, convert_chemical, convert_bioconcept, convert_bioitem
from convert_evidence import convert_literature, convert_phenotype, convert_go, \
    convert_qualifier, convert_interaction, convert_binding, \
    convert_regulation, convert_protein_domain
from convert_other import convert_bioentity_in_depth, convert_reference_in_depth, \
    convert_bioconcept_in_depth
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
     
    #Phenotype   
    try:
        convert_phenotype.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Literature
    try:
        convert_literature.convert(old_session_maker, new_session_maker)
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #GO
    try:
        convert_go.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Qualifier
    try:
        convert_qualifier.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Interaction
    try:
        convert_interaction.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Binding
    try:
        convert_binding.convert(new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Domain
    try:
        convert_protein_domain.convert(new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Regulation
    try:
        convert_regulation.convert(new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
     
    ######################### Other ##############################
       
    #Bioentity in depth
    try:
        convert_bioentity_in_depth.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )

    #Reference in depth
    try:
        convert_reference_in_depth.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
        
    #Bioconcept in depth
    try:
        convert_bioconcept_in_depth.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    