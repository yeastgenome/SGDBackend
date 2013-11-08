'''
Created on Oct 25, 2013

@author: kpaskov
'''
from convert_utils import create_or_update
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys
"""
--------------------- Convert Qualifier Evidence ---------------------
"""
    
def create_qualifier_evidence(old_bioentity, id_to_bioentity, key_to_strain, key_to_source):
    from model_new_schema.evidence import Qualifierevidence
    
    ann = old_bioentity.annotation
    if ann is None:
        return None
    qualifier = ann.qualifier
    if qualifier is None:
        return []    
    bioentity = None if old_bioentity.id not in id_to_bioentity else id_to_bioentity[old_bioentity.id]

    strain = key_to_strain['S288C']
    source = key_to_source['SGD']
        
    qualifierevidence = Qualifierevidence(source, strain, bioentity, qualifier,
                                          old_bioentity.date_created, old_bioentity.created_by)
    return [qualifierevidence]

def convert_qualifier_evidence(old_session_maker, new_session_maker):
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.evidence import Qualifierevidence as NewQualifierevidence
    from model_new_schema.evelements import Strain as NewStrain, Source as NewSource
    from model_old_schema.feature import Feature as OldFeature
    
    log = logging.getLogger('convert.qualifier.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewQualifierevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['reference_id', 'experiment_id', 'strain_id', 'source_id',
                           'bioentity_id', 'qualifier']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(NewStrain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldFeature).options(joinedload('annotation'))
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_qualifier_evidence(old_obj, id_to_bioentity, key_to_strain, key_to_source)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    obj_id = newly_created_obj.id
                    current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                    current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
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
        old_session.close()
        
    log.info('complete')
    
"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):  
    convert_qualifier_evidence(old_session_maker, new_session_maker)
    
