'''
Created on Oct 25, 2013

@author: kpaskov
'''
from convert_other.convert_auxiliary import convert_disambigs, \
    convert_chem_count
from convert_utils import set_up_logging, create_or_update, create_format_name
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys
   
   

"""
--------------------- Convert Chemical Relation ---------------------
"""

def create_chemical_relation(cvtermrel, key_to_chemical, key_to_source):
    from model_new_schema.chemical import Chemicalrelation
    
    source = key_to_source['SGD']
    
    parent_key = create_format_name(cvtermrel.parent.name)[:95]
    child_key = create_format_name(cvtermrel.child.name)[:95]
    
    parent = None
    child = None
    if parent_key in key_to_chemical:
        parent = key_to_chemical[parent_key]
    if child_key in key_to_chemical:
        child = key_to_chemical[child_key]
    
    if parent is not None and child is not None:
        return [Chemicalrelation(source, cvtermrel.relationship_type, parent, child, cvtermrel.date_created, cvtermrel.created_by)]
    else:
        return []
    
def convert_chemical_relation(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Source
    from model_new_schema.chemical import Chemicalrelation, Chemical
    from model_old_schema.cv import CVTermRel
    
    log = logging.getLogger('convert.chemical.relations')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Chemicalrelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['parent_id', 'child_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()
        
        #Grab cached dictionaries
        key_to_phenotype = dict([(x.unique_key(), x) for x in new_session.query(Chemical).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        
        old_session = old_session_maker()
        old_objs = old_session.query(CVTermRel).options(joinedload('child'), joinedload('parent')).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_chemical_relation(old_obj, key_to_phenotype, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    already_seen.add(unique_key)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                else:
                    print unique_key
                    
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
    log = set_up_logging('convert.chemical_in_depth')
    
    log.info('begin')
        
    #convert_chemical_relation(old_session_maker, new_session_maker)
    convert_chem_count(new_session_maker, 'convert.chemical.count')
            
    from model_new_schema.chemical import Chemical
    convert_disambigs(new_session_maker, Chemical, ['id', 'format_name'], 'CHEMICAL', None, 'convert.chemical.disambigs', 2000)
 
    log.info('complete')
