'''
Created on Jul 3, 2013

@author: kpaskov
'''

from convert_core import convert_reference, convert_bioentity, \
    convert_evelements, convert_chemical
from convert_evidence import convert_literature, convert_regulation, \
    convert_phenotype, convert_go, convert_binding, convert_genetic_interaction, \
    convert_physical_interaction
from convert_other import convert_protein, convert_bioentity_in_depth, \
    convert_reference_in_depth
from convert_utils import set_up_logging, prepare_schema_connection, \
    prepare_connections
from threading import Thread
import sys

if __name__ == "__main__":   
    old_session_maker, new_session_maker = prepare_connections()
    
    log = set_up_logging('convert')
    log.info('begin')
    
    ################# Core Converts ###########################
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
        
    #Chemical
    try:
        convert_chemical.convert(old_session_maker, new_session_maker)  
    except Exception:
        log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
 
    ################# Converts in parallel ###########################
     
    #Bioentity in depth
    class ConvertBioentityInDepthThread (Thread):
        def run(self):
            try:
                convert_bioentity_in_depth.convert(old_session_maker, new_session_maker)  
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertBioentityInDepthThread().start()

    #Reference in depth
    class ConvertReferenceInDepthThread(Thread):
        def run(self):
            try:
                convert_reference_in_depth.convert(old_session_maker, new_session_maker)  
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertReferenceInDepthThread().start()
       
    #Protein
    class ConvertProteinThread(Thread):
        def run(self):
            try:
                convert_protein.convert(old_session_maker, new_session_maker)  
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertProteinThread().start()
        
    #Regulation
    class ConvertRegulationThread(Thread):
        def run(self):
            try:
                convert_regulation.convert(new_session_maker)  
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertRegulationThread().start()
        
    #Phenotype and Genetic Interaction
    class ConvertPhenotypeGeninteractionThread(Thread):
        def run(self):
            try:
                convert_phenotype.convert(old_session_maker, new_session_maker)  
                convert_genetic_interaction.convert(old_session_maker, new_session_maker)
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertPhenotypeGeninteractionThread().start()

    
    #Physical Interaction
    class ConvertPhysicalInteractionThread(Thread):
        def run(self):
            try:
                convert_physical_interaction.convert(old_session_maker, new_session_maker)
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertPhysicalInteractionThread().start()
        
    #Literature
    class ConvertLiteratureThread(Thread):
        def run(self):
            try:
                convert_literature.convert(old_session_maker, new_session_maker)
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertLiteratureThread().start()
        
    #GO
    class ConvertGoThread(Thread):
        def run(self):
            try:
                convert_go.convert(old_session_maker, new_session_maker)  
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertGoThread().start()
        
    #Binding
    class ConvertBindingThread(Thread):
        def run(self):
            try:
                convert_binding.convert(new_session_maker)  
            except Exception:
                log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    ConvertBindingThread().start()
    
    
    