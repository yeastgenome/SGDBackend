'''
Created on Jul 3, 2013

@author: kpaskov
'''
from convert_aux.auxillary_tables import convert_bioentity_reference
from convert_utils import create_or_update, set_up_logging, prepare_schema_connection
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func, or_
import logging
import model_new_schema
import model_old_schema
import sys

"""
--------------------- Convert Physical Interaction Evidence ---------------------
"""

def create_litevidence_id(old_litevidence_id):
    return old_litevidence_id - 243284 + 30000000

def create_litevidence(old_litevidence, reference_ids, bioent_ids):
    from model_new_schema.literature import Literatureevidence as NewLiteratureevidence
    
    reference_id = old_litevidence.litguide.reference_id
    if reference_id not in reference_ids:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    bioentity_id = old_litevidence.feature_id
    if bioentity_id not in bioent_ids:
        return None
    
    new_id = create_litevidence_id(old_litevidence.id)
    topic = old_litevidence.litguide.topic
    
    new_litevidence = NewLiteratureevidence(new_id, reference_id, bioentity_id, topic,
                                           old_litevidence.date_created, old_litevidence.created_by)
    return [new_litevidence]

def convert_litevidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.literature import Literatureevidence as NewLiteratureevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_old_schema.reference import LitguideFeat as OldLitguideFeat
    
    log = logging.getLogger('convert.literature.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'class_type', 'strain_id',
                       'source', 'topic', 'bioentity_id', 'date_created', 'created_by']
        
        
        #Grab cached dictionaries
        bioent_ids = set([x.id for x in new_session.query(NewBioentity).all()])
        reference_ids = set([x.id for x in new_session.query(NewReference).all()])
        
        min_id = old_session.query(func.min(OldLitguideFeat.id)).first()[0]
        count = old_session.query(func.max(OldLitguideFeat.id)).first()[0] - min_id
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(NewLiteratureevidence).filter(NewLiteratureevidence.id >= create_litevidence_id(min_id)).filter(NewLiteratureevidence.id < create_litevidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects                  
            old_objs = old_session.query(OldLitguideFeat).filter(
                                                OldLitguideFeat.id >= min_id).filter(
                                                OldLitguideFeat.id < min_id+chunk_size).filter(
                                                or_(OldLitguideFeat.topic=='Additional Literature',
                                                    OldLitguideFeat.topic=='Primary Literature',
                                                    OldLitguideFeat.topic=='Omics',
                                                    OldLitguideFeat.topic=='Reviews')).options(
                                                joinedload('litguide')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_litevidence(old_obj, reference_ids, bioent_ids)
                    
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

def convert(old_session_maker, new_session_maker):
    log = set_up_logging('convert.literature')
    
    log.info('begin')
    
    convert_litevidence(old_session_maker, new_session_maker, 100000)
    
    from model_new_schema.literature import Literatureevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'PRIMARY_LITERATURE', 'convert.literature.primary_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Primary Literature')
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'ADDITIONAL_LITERATURE', 'convert.literature.additional_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Additional Literature')
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'OMICS_LITERATURE', 'convert.literature.omics_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Omics')
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'REVIEW_LITERATURE', 'convert.literature.review_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Reviews')
    
    log.info('complete')

if __name__ == "__main__":
    from convert_all import new_config, old_config
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker, False)