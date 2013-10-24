'''
Created on Feb 27, 2013

@author: kpaskov
'''
from convert_aux.convert_aux_other import convert_bioentity_reference, \
    convert_disambigs
from convert_utils import set_up_logging, create_or_update, prepare_connections
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
import logging
import sys

"""
--------------------- Convert GO ---------------------
"""

abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}
def create_go(old_go, key_to_source):
    from model_new_schema.go import Go as NewGo
    
    display_name = old_go.go_term
    source = key_to_source['GO']
    new_go = NewGo(display_name, source, None, old_go.go_definition,
                   old_go.go_go_id, abbrev_to_go_aspect[old_go.go_aspect],  
                   old_go.date_created, old_go.created_by)
    return [new_go]

def convert_go(old_session_maker, new_session_maker):
    from model_new_schema.go import Go as NewGo
    from model_new_schema.evelement import Source as NewSource
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
        values_to_check = ['go_id', 'go_aspect', 'display_name', 'link', 'sgdid', 'description', 'source_id']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
                
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        old_objs = old_session.query(OldGo).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_go(old_obj, key_to_source)
                
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
        old_session.close()
        
    log.info('complete')

"""
--------------------- Convert Evidence ---------------------
"""

def create_evidence(old_go_feature, key_to_go, id_to_bioentity, id_to_reference, key_to_source):
    from model_new_schema.go import Goevidence as NewGoevidence
    
    evidences = []
    
    go_key = ('GO:' + str(old_go_feature.go.go_go_id), 'GO')
    go = None if go_key not in key_to_go else key_to_go[go_key]
        
    bioent_id = old_go_feature.feature_id
    bioent = None if bioent_id not in id_to_bioentity else id_to_bioentity[bioent_id]
    if bioent is None:
        print bioent_id
        return []
        
    source = key_to_source['SGD']
            
    old_go_refs = old_go_feature.go_refs
    for old_go_ref in old_go_refs:        
        reference_id = old_go_ref.reference_id
        reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    
        qualifier = None
        if old_go_ref.go_qualifier is not None:
            qualifier = old_go_ref.qualifier
            
        new_evidence = NewGoevidence(source, reference, None, bioent, go,
                                old_go_feature.go_evidence, old_go_feature.annotation_type, qualifier, old_go_feature.date_last_reviewed, 
                                old_go_ref.date_created, old_go_ref.created_by)
        evidences.append(new_evidence)
    return evidences

def convert_evidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.go import Goevidence as NewGoevidence
    from model_new_schema.evelement import Source as NewSource
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.go import Go as NewGo
    from model_old_schema.go import GoFeature as OldGoFeature
    
    log = logging.getLogger('convert.go.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id',
                       'go_evidence', 'annotation_type', 'date_last_reviewed', 'qualifier',
                       'bioentity_id', 'bioconcept_id']
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_go = dict([(x.unique_key(), x) for x in new_session.query(NewGo).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
                
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        for i in range(0, num_chunks+1):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
            
            #Grab all current objects
            current_objs = new_session.query(NewGoevidence).filter(NewGoevidence.bioentity_id >= min_id).filter(NewGoevidence.bioentity_id < max_id).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            already_seen_obj = set()
            
            #Grab old objects
            old_objs = old_session.query(OldGoFeature).filter(
                                OldGoFeature.feature_id >= min_id).filter(
                                OldGoFeature.feature_id < min_id+chunk_size).options(
                                    joinedload('go_refs'),
                                    joinedload('go_refs.go_qualifier')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, key_to_go, id_to_bioentity, id_to_reference, key_to_source)
                    
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    if obj_key not in already_seen_obj:
                        obj_id = newly_created_obj.id
                        current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                        current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        already_seen_obj.add(obj_key)
                    else:
                        print obj_key
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
    
            #Commit
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
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
    log = set_up_logging('convert.go')
    
    log.info('begin')
        
    convert_go(old_session_maker, new_session_maker) 
    
    convert_evidence(old_session_maker, new_session_maker, 500)
    
    from model_new_schema.go import Goevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Goevidence, 'GO', 'convert.go.bioentity_reference', 10000, get_bioent_ids_f)

    from model_new_schema.go import Go
    convert_disambigs(new_session_maker, Go, ['id', 'format_name'], 'BIOCONCEPT', 'GO', 'convert.go.disambigs', 2000)
    
    log.info('complete')
            
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)
    

    
            
        
            
            
            
            
            