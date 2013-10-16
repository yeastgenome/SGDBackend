'''
Created on May 31, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, prepare_connections
from convert_utils.link_maker import bioent_link
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys

#Recorded times: 
#Maitenance (cherry-vm08): 2:56, 2:59 
#First Load (sgd-ng1): 4:08, 3:49
#Maitenance (sgd-ng1): 4:17

"""
--------------------- Convert Locus ---------------------
"""

def create_locus_type(old_feature_type):
    bioentity_type = old_feature_type.upper()
    bioentity_type = bioentity_type.replace (" ", "_")
    return bioentity_type

def create_locus(old_bioentity):
    from model_new_schema.bioentity import Locus
    
    locus_type = create_locus_type(old_bioentity.type)
    if locus_type is None:
        return None
    
    display_name = old_bioentity.gene_name
    if display_name is None:
        display_name = old_bioentity.name
    
    format_name = old_bioentity.name.upper()
    link = bioent_link('LOCUS', format_name)
    
    attribute = None
    short_description = None
    headline = None
    description = None
    genetic_position = None
    
    ann = old_bioentity.annotation
    if ann is not None:
        attribute = ann.attribute
        short_description = ann.name_description
        headline = ann.headline
        description = ann.description
        genetic_position = ann.genetic_position
    
    bioentity = Locus(old_bioentity.id, display_name, format_name,  old_bioentity.dbxref_id, link, old_bioentity.source, old_bioentity.status, 
                         locus_type, attribute, short_description, headline, description, genetic_position, 
                         old_bioentity.date_created, old_bioentity.created_by)
    return [bioentity]

def convert_locus(old_session_maker, new_session_maker):
    from model_new_schema.bioentity import Locus as NewLocus
    from model_old_schema.feature import Feature as OldFeature
    
    log = logging.getLogger('convert.bioentity.locus')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewLocus).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'link', 'source', 'status', 'date_created', 'created_by',
                       'attribute', 'name_description', 'headline', 'description',  'dbxref',
                       'genetic_position', 'locus_type']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldFeature).options(joinedload('annotation')).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_locus(old_obj)
                
            if newly_created_objs is not None:
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
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    output_creator.finished()
    
"""
--------------------- Convert Protein ---------------------
"""

def create_protein_id(old_feature_id):
    return old_feature_id + 200000

def create_protein(old_protein, id_to_bioentity):
    from model_new_schema.protein import Protein
    
    locus_id = old_protein.feature_id
    if locus_id not in id_to_bioentity:
        print 'Bioentity does not exist. ' + str(locus_id)
    locus = id_to_bioentity[locus_id]
    
    display_name = locus.display_name + 'p'
    format_name = locus.format_name + 'P'
    link = locus.link.replace('/locus.f', '/protein/proteinPage.')
    protein = Protein(create_protein_id(locus_id), display_name, format_name, None,  link, locus_id, old_protein.length, 
                      old_protein.n_term_seq, old_protein.c_term_seq, old_protein.date_created, old_protein.created_by)
    return [protein]

def convert_protein(old_session_maker, new_session_maker):
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.protein import Protein as NewProtein
    from model_old_schema.sequence import ProteinInfo as OldProteinInfo
    
    log = logging.getLogger('convert.bioentity.protein')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewProtein).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'link', 'source', 'status', 'date_created', 'created_by', 'link',
                       'locus_id', 'length', 'n_term_seq', 'c_term_seq']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldProteinInfo).all()
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])       
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_protein(old_obj, id_to_bioentity)
                
            if newly_created_objs is not None:
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
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    output_creator.finished()
    

"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):  
    log = set_up_logging('convert.bioentity')
    
    log.info('begin')
        
    convert_locus(old_session_maker, new_session_maker)

    convert_protein(old_session_maker, new_session_maker)
        
    log.info('complete')
    
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)   
   

