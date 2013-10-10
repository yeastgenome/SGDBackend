'''
Created on May 6, 2013

@author: kpaskov
'''
from convert_aux.auxillary_tables import convert_bioentity_reference
from convert_utils import create_or_update, set_up_logging, prepare_schema_connection, \
    create_format_name
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
import logging
import model_new_schema
import model_old_schema
import sys

'''
 This code is used to convert interaction data from the old schema to the new. It does this by
 creating new schema objects from the old, then comparing these new objects to those already
 stored in the new database. If a newly created object matches one that is already stored, the two
 are compared and the database fields are updated. If a newly created object does not match one that is 
 already stored, it is added to the database.
'''

"""
--------------------- Convert Physical Interaction Evidence ---------------------
"""

def create_physical_evidence_id(old_evidence_id):
    return old_evidence_id - 397664 + 20000000

def create_physical_interevidence(old_interaction, key_to_experiment,
                         reference_ids, bioent_ids):
    from model_new_schema.interaction import Physinteractionevidence as NewPhysinteractionevidence
    if old_interaction.interaction_type == 'physical interactions':    
        reference_ids = old_interaction.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        note = old_interaction.interaction_references[0].note
        
        if reference_id not in reference_ids:
            print 'Reference does not exist.'
            return None
        
        bioent_ids = list(old_interaction.feature_ids)
        bioent_ids.sort()
        bioent1_id = bioent_ids[0]
        bioent2_id = bioent_ids[1]
        
        if bioent1_id > bioent2_id:
            print 'Out of order.'
            return None
        if bioent1_id not in bioent_ids:
            print 'Bioentity does not exist.'
            return None
        if bioent2_id not in bioent_ids:
            print 'Bioentity does not exist.'
            return None
        
        experiment_key = create_format_name(old_interaction.experiment_type)
        if experiment_key not in key_to_experiment:
            print 'Experiment does not exist. ' + str(experiment_key)
            return None
        experiment_id = key_to_experiment[experiment_key].id
            
        feat_interacts = sorted(old_interaction.feature_interactions, key=lambda x: x.feature_id)
        bait_hit = '-'.join([x.action for x in feat_interacts])
            
        new_physical_interevidence = NewPhysinteractionevidence(create_physical_evidence_id(old_interaction.id), experiment_id, reference_id, None, old_interaction.source,
                                                             bioent1_id, bioent2_id,
                                                             old_interaction.annotation_type,  old_interaction.modification, bait_hit, note,
                                                             old_interaction.date_created, old_interaction.created_by)
        return [new_physical_interevidence]
    return None

def convert_physical_interevidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.interaction import Physinteractionevidence as NewPhysinteractionevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.evelement import Experiment as NewExperiment
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_old_schema.interaction import Interaction as OldInteraction
    
    log = logging.getLogger('convert.physical_interaction.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source',
                       'bioentity1_id', 'bioentity2_id',
                       'modification', 'note', 'annotation_type', 'date_created', 'created_by']
        
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        bioent_ids = set([x.id for x in new_session.query(NewBioentity).all()])
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        min_id = old_session.query(func.min(OldInteraction.id)).first()[0]
        count = old_session.query(func.max(OldInteraction.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewPhysinteractionevidence).filter(NewPhysinteractionevidence.id >= create_physical_evidence_id(min_id)).filter(NewPhysinteractionevidence.id < create_physical_evidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects
            old_objs = old_session.query(OldInteraction).filter(
                                                OldInteraction.id >= min_id).filter(
                                                OldInteraction.id < min_id+chunk_size).options(
                                                    joinedload('interaction_references'),
                                                    joinedload('feature_interactions')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_physical_interevidence(old_obj, key_to_experiment, reference_ids, bioent_ids)
                    
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
    log = set_up_logging('convert.physical_interaction')
    
    log.info('begin')
    
    convert_physical_interevidence(old_session_maker, new_session_maker, 10000)
        
    from model_new_schema.interaction import Physinteractionevidence
    get_bioent_ids_f = lambda x: [x.bioentity1_id, x.bioentity2_id]
    convert_bioentity_reference(new_session_maker, Physinteractionevidence, 'PHYSINTERACTION', 'convert.physical_interaction.bioentity_reference', 10000, get_bioent_ids_f)
           
    log.info('complete')
    
if __name__ == "__main__":
    from convert_all import new_config, old_config
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)   
   
    
