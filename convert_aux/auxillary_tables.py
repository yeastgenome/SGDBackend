'''
Created on May 28, 2013

@author: kpaskov
'''
from convert_utils import create_or_update
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
import logging
import sys

"""
--------------------- Convert Bioentity Reference ---------------------
"""

def create_bioentity_reference(evidence, get_bioent_ids_f, class_type):
    from model_new_schema.auxiliary import BioentityReference as NewBioentityReference
    
    bioentity_references = []
    reference_id = evidence.reference_id
    if reference_id is not None:
        for bioent_id in get_bioent_ids_f(evidence):
            bioentity_references.append(NewBioentityReference(class_type, bioent_id, reference_id))
    return bioentity_references

def create_bioentity_reference_from_paragraph(paragraph, class_type):
    from model_new_schema.auxiliary import BioentityReference as NewBioentityReference
    
    bioentity_references = []
    bioent_id = paragraph.bioentity_id
    for reference in paragraph.references:
        bioentity_references.append(NewBioentityReference(class_type, bioent_id, reference.id))
    return bioentity_references

def convert_bioentity_reference(new_session_maker, evidence_class, class_type, label, chunk_size, get_bioent_ids_f, 
                                filter_f=None):
    from model_new_schema.auxiliary import BioentityReference
    from model_new_schema.bioentity import Paragraph
    
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = []     
        
        #Grab all current objects
        current_objs = new_session.query(BioentityReference).filter(BioentityReference.class_type == class_type).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        used_unique_keys = set()   
        
        min_id = new_session.query(func.min(evidence_class.id)).first()[0]
        count = new_session.query(func.max(evidence_class.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            old_objs = new_session.query(evidence_class).filter(evidence_class.id >= min_id, evidence_class.id <= min_id+chunk_size).all()
        
            for old_obj in old_objs:
                if filter_f is None or filter_f(old_obj):
                    #Convert old objects into new ones
                    newly_created_objs = create_bioentity_reference(old_obj, get_bioent_ids_f, class_type)
             
                    if newly_created_objs is not None:
                        #Edit or add new objects
                        for newly_created_obj in newly_created_objs:
                            unique_key = newly_created_obj.unique_key()
                            if unique_key not in used_unique_keys:
                                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                                current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                                used_unique_keys.add(unique_key)
                                
                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
            
        #Add paragraph-related bioent_references.
        old_objs = new_session.query(Paragraph).filter(Paragraph.class_type == class_type).options(joinedload('paragraph_references')).all()                               
        for old_obj in old_objs:
            if filter_f is None or filter_f(old_obj):
                #Convert old objects into new ones
                newly_created_objs = create_bioentity_reference_from_paragraph(old_obj, class_type)
         
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        if unique_key not in used_unique_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            used_unique_keys.add(unique_key)
                            
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
--------------------- Convert Disambigs ---------------------
"""

def create_disambigs(obj, fields, class_type, subclass_type):
    from model_new_schema.auxiliary import Disambig
    
    field_values = set(filter(None, [getattr(obj, field) for field in fields]))
    disambigs = []
    for field_value in field_values:
        disambigs.append(Disambig(str(field_value), class_type, subclass_type, obj.id))
    return disambigs

def convert_disambigs(new_session_maker, cls, fields, class_type, subclass_type, label, chunk_size):
    from model_new_schema.auxiliary import Disambig
    
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = []     
        
        #Grab all current objects
        current_objs = new_session.query(Disambig).filter(Disambig.class_type == class_type).filter(Disambig.subclass_type == subclass_type).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
        untouched_obj_ids = set(id_to_current_obj.keys())
                
        min_id = new_session.query(func.min(cls.id)).first()[0]
        count = new_session.query(func.max(cls.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            old_objs = new_session.query(cls).filter(cls.id >= min_id, cls.id < min_id+chunk_size).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_disambigs(old_obj, fields, class_type, subclass_type)
         
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
            
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
    
    