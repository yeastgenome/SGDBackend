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
    from model_new_schema.paragraph import Paragraph
    
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

def is_number(str_value):
    try:
        int(str_value)
        return True
    except:
        return False

def create_disambigs(obj, fields, class_type, subclass_type):
    from model_new_schema.auxiliary import Disambig
    
    field_values = set()
    for field in fields:
        field_value = getattr(obj, field)
        if field_value is not None and (field == 'id' or not is_number(field_value)):
            field_values.add(field_value)
    
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
    
"""
--------------------- Convert Biofact ---------------------
"""

def create_biofact(evidence, id_to_bioentity, id_to_bioconcept):
    from model_new_schema.auxiliary import Biofact as NewBiofact
    
    bioentity = None if evidence.bioentity_id not in id_to_bioentity else id_to_bioentity[evidence.bioentity_id]
    bioconcept = None if evidence.bioconcept_id not in id_to_bioconcept else id_to_bioconcept[evidence.bioconcept_id]
    
    return [NewBiofact(bioentity, bioconcept)]

def convert_biofact(new_session_maker, evidence_class, bioconcept_class, bioconcept_class_type, label, chunk_size, 
                                filter_f=None):
    from model_new_schema.auxiliary import Biofact
    from model_new_schema.bioentity import Bioentity
    
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = []     
        
        #Grab all current objects
        current_objs = new_session.query(Biofact).filter(Biofact.bioconcept_class_type == bioconcept_class_type).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Cache
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(Bioentity).all()])
        id_to_bioconcept = dict([(x.id, x) for x in new_session.query(bioconcept_class).all()])
            
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
                    newly_created_objs = create_biofact(old_obj, id_to_bioentity, id_to_bioconcept)
             
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
--------------------- Convert Interaction ---------------------
"""

def create_interaction_id(evidence_id):
    return evidence_id

def create_directed_key(evidence):
    return create_directed_key_from_bioents(evidence.bioentity1_id, evidence.bioentity2_id)

def create_directed_key_from_bioents(bioent1_id, bioent2_id):
    return (bioent1_id, bioent2_id)    
    
def create_undirected_interaction_format_name(evidence, id_to_bioent):
    bioent1_id = evidence.bioentity1_id
    bioent2_id = evidence.bioentity2_id
    return create_undirected_interaction_format_name_from_bioents(bioent1_id, bioent2_id, id_to_bioent)
    
def create_undirected_interaction_format_name_from_bioents(bioent1_id, bioent2_id, id_to_bioent):
    bioent1 = id_to_bioent[bioent1_id]
    bioent2 = id_to_bioent[bioent2_id]
    
    if bioent1.id < bioent2.id:
        return str(bioent1.format_name + '__' + bioent2.format_name)
    else:
        return str(bioent2.format_name + '__' + bioent1.format_name)

def create_interaction(evidence, evidence_count, id_to_bioent, directed):
    from model_new_schema.auxiliary import Interaction
    bioent1_id = evidence.bioentity1_id
    bioent2_id = evidence.bioentity2_id
    if directed:
        bioent1_id, bioent2_id = create_directed_key(evidence)
        format_name = id_to_bioent[bioent1_id] + '__' + id_to_bioent[bioent2_id]
    else:
        format_name = create_undirected_interaction_format_name(evidence, id_to_bioent)
    interaction = Interaction(create_interaction_id(evidence.id), evidence.class_type, format_name, format_name, bioent1_id, bioent2_id)
    interaction.evidence_count = evidence_count
    return [interaction]

def interaction_precomp(format_name_to_evidence_count, more_evidences, id_to_bioent, directed):
    for evidence in more_evidences:
        if directed:
            format_name = create_directed_key(evidence)
        else:
            format_name = create_undirected_interaction_format_name(evidence, id_to_bioent)
            
        
        if format_name in format_name_to_evidence_count:
            format_name_to_evidence_count[format_name] = format_name_to_evidence_count[format_name] + 1
        else:
            format_name_to_evidence_count[format_name] = 1

def convert_interaction(new_session_maker, evidence_class, class_type,  label, chunk_size, directed):
    from model_new_schema.auxiliary import Interaction
    from model_new_schema.bioentity import Bioentity
    
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['display_name', 'bioentity1_id', 'bioentity2_id', 'evidence_count']   
        
        #Grab all current objects
        current_objs = new_session.query(Interaction).filter(Interaction.class_type == class_type).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Grab cached dictionaries
        id_to_bioent = dict([(x.id, x) for x in new_session.query(Bioentity).all()])
            
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        used_unique_keys = set()   
        
        #Precomp evidence count
        format_name_to_evidence_count = {}
        min_id = new_session.query(func.min(evidence_class.id)).first()[0]
        count = new_session.query(func.max(evidence_class.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):  
            more_old_objs = new_session.query(evidence_class).filter(evidence_class.id >= min_id).filter(evidence_class.id < min_id+chunk_size).all()
            interaction_precomp(format_name_to_evidence_count, more_old_objs, id_to_bioent, directed)
            min_id = min_id + chunk_size

        #Create interactions
        min_id = new_session.query(func.min(evidence_class.id)).first()[0]
        count = new_session.query(func.max(evidence_class.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):  
            old_objs = new_session.query(evidence_class).filter(evidence_class.id >= min_id).filter(evidence_class.id < min_id+chunk_size).all()    
            for old_obj in old_objs:
                #Convert old objects into new ones
                if directed:
                    format_name = create_directed_key(old_obj)
                else:
                    format_name = create_undirected_interaction_format_name(old_obj, id_to_bioent)
                evidence_count = format_name_to_evidence_count[format_name]
                newly_created_objs = create_interaction(old_obj, evidence_count, id_to_bioent, directed)
         
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
    
    