'''
Created on Oct 25, 2013

@author: kpaskov
'''
from convert_other.convert_auxiliary import convert_disambigs
from convert_utils import create_or_update
from convert_utils.output_manager import OutputCreator
import logging
import sys
   
   
"""
--------------------- Convert ECNumber Relation ---------------------
"""

def create_ecnumber_relation(ecnumber, key_to_ecnumber, key_to_source):
    from model_new_schema.bioconcept import Bioconceptrelation as NewBioconceptrelation
    
    source = key_to_source['IUBMB']
    
    format_name = ecnumber.format_name
    pieces = format_name.split('.')
    i = 1
    done = False
    while not done:
        if pieces[-i] != '-':
            pieces[-i] = '-'
            done = True
        i = i+1
    parent_format_name = ('.'.join(pieces), 'EC_NUMBER')
    parent = None if parent_format_name not in key_to_ecnumber else key_to_ecnumber[parent_format_name]
    if parent is None:
        print parent_format_name
        return []
    return [NewBioconceptrelation(source, None, parent, ecnumber, 'EC_NUMBER', None, None)]

def convert_ecnumber_relation(new_session_maker):
    from model_new_schema.evelements import Source
    from model_new_schema.bioconcept import Bioconceptrelation, ECNumber
    
    log = logging.getLogger('convert.bioconcept.ecnumber_relations')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Bioconceptrelation).filter(Bioconceptrelation.bioconrel_class_type == 'EC_NUMBER').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['parent_id', 'child_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_ecnumber = dict([(x.unique_key(), x) for x in new_session.query(ECNumber).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        
        for old_obj in key_to_ecnumber.values():
            #Convert old objects into new ones
            newly_created_objs = create_ecnumber_relation(old_obj, key_to_ecnumber, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()
        
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        
    log.info('complete')
    
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):  
    convert_ecnumber_relation(new_session_maker)
            
    from model_new_schema.bioconcept import Phenotype
    convert_disambigs(new_session_maker, Phenotype, ['id', 'format_name'], 'BIOCONCEPT', 'PHENOTYPE', 'convert.phenotype.disambigs', 2000)
 
    from model_new_schema.bioconcept import Go
    convert_disambigs(new_session_maker, Go, ['id', 'format_name'], 'BIOCONCEPT', 'GO', 'convert.go.disambigs', 2000)
        
