'''
Created on Jul 3, 2013

@author: kpaskov
'''

#1.23.14 Maitenance (sgd-dev): 1:15:15

from convert_other.convert_auxiliary import convert_bioentity_reference
from convert_utils import create_or_update
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
import logging
import sys

"""
--------------------- Convert Physical Interaction Evidence ---------------------
"""

def create_litevidence(old_litevidence, id_to_reference, id_to_bioentity, key_to_source):
    from model_new_schema.evidence import Literatureevidence as NewLiteratureevidence
    
    reference_id = old_litevidence.litguide.reference_id
    reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]

    bioentity_id = old_litevidence.feature_id
    bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]
    
    if reference is None:
        print 'Reference not found: ' + str(reference_id)
        return []
    if bioentity is None:
        print 'Bioentity not found: ' + str(bioentity_id)
        return []
    
    source = key_to_source['SGD']
    
    topic = old_litevidence.litguide.topic
    
    new_litevidence = NewLiteratureevidence(source, reference, None, bioentity, topic,
                                           old_litevidence.date_created, old_litevidence.created_by)
    return [new_litevidence]

def convert_litevidence(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.evidence import Literatureevidence as NewLiteratureevidence
    from model_new_schema.reference import Reference as NewReference
    from model_new_schema.evelements import Source as NewSource
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
                       'source_id', 'topic', 'bioentity_id']
        
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        for i in range(0, num_chunks+1):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
       
            #Grab all current objects
            current_objs = new_session.query(NewLiteratureevidence).filter(NewLiteratureevidence.bioentity_id >= min_id).filter(NewLiteratureevidence.bioentity_id < max_id).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())
            
            #Grab old objects                  
            old_objs = old_session.query(OldLitguideFeat).filter(
                                                OldLitguideFeat.feature_id >= min_id).filter(
                                                OldLitguideFeat.feature_id < max_id).filter(
                                                or_(OldLitguideFeat.topic=='Additional Literature',
                                                    OldLitguideFeat.topic=='Primary Literature',
                                                    OldLitguideFeat.topic=='Omics',
                                                    OldLitguideFeat.topic=='Reviews')).options(
                                                joinedload('litguide')).all()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_litevidence(old_obj, id_to_reference, id_to_bioentity, key_to_source)
                    
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
    convert_litevidence(old_session_maker, new_session_maker, 200)
    
    from model_new_schema.evidence import Literatureevidence
    get_bioent_ids_f = lambda x: [x.bioentity_id]
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'PRIMARY_LITERATURE', 'convert.literature.primary_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Primary Literature')
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'ADDITIONAL_LITERATURE', 'convert.literature.additional_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Additional Literature')
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'OMICS_LITERATURE', 'convert.literature.omics_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Omics')
    convert_bioentity_reference(new_session_maker, Literatureevidence, 'REVIEW_LITERATURE', 'convert.literature.review_bioentity_reference', 
                                100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Reviews')
    
