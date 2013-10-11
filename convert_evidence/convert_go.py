'''
Created on Feb 27, 2013

@author: kpaskov
'''
from convert_aux.auxillary_tables import convert_bioentity_reference
from convert_utils import set_up_logging, create_or_update, \
    prepare_connections
from convert_utils.link_maker import biocon_link
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
import logging
import sys

"""
--------------------- Convert GO ---------------------
"""

def create_go_id(old_go_id):
    return old_go_id + 50000000

abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go):
    from model_new_schema.go import Go as NewGo
    
    display_name = old_go.go_term
    format_name = str(old_go.go_go_id)
    link = biocon_link('GO', format_name)
    new_go = NewGo(create_go_id(old_go.id), display_name, format_name, link, old_go.go_definition,
                   old_go.go_go_id, abbrev_to_go_aspect[old_go.go_aspect],  
                   old_go.date_created, old_go.created_by)
    return [new_go]

def convert_go(old_session_maker, new_session_maker):
    from model_new_schema.go import Go as NewGo
    from model_old_schema.go import Go as OldGo
    
    log = logging.getLogger('convert.go.go')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewGo).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['go_go_id', 'go_aspect', 'display_name', 'link', 'description', 'date_created', 'created_by']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        keys_already_seen = set()
            
        #Grab old objects
        old_objs = old_session.query(OldGo).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_go(old_obj)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    key = newly_created_obj.unique_key()
                    if key not in keys_already_seen:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        keys_already_seen.add(key)
                        
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
--------------------- Convert Evidence ---------------------
"""

def create_evidence_id(old_evidence_id):
    return old_evidence_id + 50000000

def create_evidence(old_go_ref, key_to_go, reference_ids, bioent_ids):
    from model_new_schema.go import Goevidence as NewGoevidence
    
    old_go_feature = old_go_ref.go_annotation
    
    go_key = (str(old_go_feature.go.go_go_id), 'GO')
    if go_key not in key_to_go:
        print 'Go term does not exist. ' + str(go_key)
        return None
    biocon_id = key_to_go[go_key].id
    
    bioent_id = old_go_feature.feature_id
    if bioent_id not in bioent_ids:
        print 'Bioentity does not exist. ' + str(bioent_id)
        return None
        
    evidence_id = create_evidence_id(old_go_ref.id)
        
    reference_id = old_go_ref.reference_id
    if reference_id not in reference_ids:
        print 'Reference does not exist. ' + str(reference_id)
        return None

    qualifier = None
    if old_go_ref.go_qualifier is not None and old_go_ref.qualifier is not None:
        qualifier = old_go_ref.qualifier
    new_evidence = NewGoevidence(evidence_id, reference_id, old_go_feature.source,
                            old_go_feature.go_evidence, old_go_feature.annotation_type, qualifier, old_go_feature.date_last_reviewed, 
                            bioent_id, biocon_id, old_go_ref.date_created, old_go_ref.created_by)
    return [new_evidence]

def convert_evidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.go import Goevidence as NewGoevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.go import Go as NewGo
    from model_old_schema.go import GoRef as OldGoRef
    
    log = logging.getLogger('convert.go.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source',
                       'go_evidence', 'annotation_type', 'date_last_reviewed', 'qualifier',
                       'bioentity_id', 'bioconcept_id', 'date_created', 'created_by']
        
        #Grab cached dictionaries
        bioent_ids = set([x.id for x in new_session.query(NewBioentity).all()])
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        key_to_go = dict([(x.unique_key(), x) for x in new_session.query(NewGo).all()])
        
        already_used_keys = set()
        
        min_id = old_session.query(func.min(OldGoRef.id)).first()[0]
        count = old_session.query(func.max(OldGoRef.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewGoevidence).filter(NewGoevidence.id >= create_evidence_id(min_id)).filter(NewGoevidence.id < create_evidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects
            old_objs = old_session.query(OldGoRef).filter(
                                OldGoRef.id >= min_id).filter(
                                OldGoRef.id < min_id+chunk_size).options(
                                    joinedload('go_annotation')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, key_to_go, reference_ids, bioent_ids)
                    
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        key = newly_created_obj.unique_key()
                        if key not in already_used_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            already_used_keys.add(key)
                            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
    
            #Commit
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
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
    log = set_up_logging('convert.go')
    
    log.info('begin')
        
    #convert_go(old_session_maker, new_session_maker) 
    
    convert_evidence(old_session_maker, new_session_maker, 10000)
    
    from model_new_schema.go import Goevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Goevidence, 'GO', 'convert.go.bioentity_reference', 10000, get_bioent_ids_f)

    log.info('complete')
            
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)
    

    
            
        
            
            
            
            
            