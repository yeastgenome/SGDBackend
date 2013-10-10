'''
Created on Sep 23, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, prepare_schema_connection, create_format_name, break_up_file
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
import logging
import model_new_schema
import sys

"""
--------------------- Convert Evidence ---------------------
"""
def create_evidence_id(old_regevidence_id):
    return old_regevidence_id + 90000000

def create_evidence(row, row_id, key_to_experiment, key_to_bioent, pubmed_to_reference_id):
    from model_new_schema.sequence import Bindingevidence
    
    bioent_format_name = row[2][1:-1]
    motif_id = row[3][1:-1]
    total_score = row[6][1:-1]
    expert_confidence = row[8][1:-1]
    experiment_format_name = create_format_name(row[9][1:-1])
    pubmed_id = int(row[10][1:-1])
    source = 'YeTFaSCo'
    
    if expert_confidence != 'High':
        return None
    
    if (bioent_format_name, 'LOCUS') in key_to_bioent:
        bioent1 = key_to_bioent[(bioent_format_name, 'LOCUS')]
    elif (bioent_format_name, 'BIOENTITY') in key_to_bioent:
        bioent1 = key_to_bioent[(bioent_format_name, 'BIOENTITY')]
    else:
        print 'Bioent does not exist ' + str(bioent_format_name)
        return None
    bioent_id = bioent1.id
    
    experiment_key = experiment_format_name
    if experiment_key not in key_to_experiment:
        print 'Experiment does not exist ' + str(experiment_key)
        return None
    experiment_id = key_to_experiment[experiment_key].id
    
    reference_id = None
    if pubmed_id in pubmed_to_reference_id:
        reference_id = pubmed_to_reference_id[pubmed_id]
    
    img_url = "/static/img/yetfasco/" + bioent_format_name + "_" + motif_id + ".0.png"
    
    new_evidence = Bindingevidence(create_evidence_id(row_id), experiment_id, reference_id, None, source, 
                                   bioent_id, total_score, expert_confidence, img_url, motif_id, None, None)
    return [new_evidence]

def convert_evidence(new_session_maker, chunk_size):
    from model_new_schema.sequence import Bindingevidence
    from model_new_schema.evelement import Experiment
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.reference import Reference
    
    log = logging.getLogger('convert.binding.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source', 'motif_id',
                       'bioentity_id', 'total_score', 'expert_confidence', 'img_url', 'date_created', 'created_by']
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(Experiment).all()])
        key_to_bioent = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        pubmed_to_reference_id = dict([(x.pubmed_id, x.id) for x in new_session.query(Reference).all()])
        
        #Grab old objects
        data = break_up_file('/Users/kpaskov/final/yetfasco_data.txt', delimeter=';')
                
        count = len(data)
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        j = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(Bindingevidence).filter(Bindingevidence.id >= create_evidence_id(min_id)).filter(Bindingevidence.id < create_evidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())

            old_objs = data[min_id:min_id+chunk_size]
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, j, key_to_experiment, key_to_bioent, pubmed_to_reference_id)
         
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
                j = j + 1
                
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
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

def convert(new_session_maker):
    log = set_up_logging('convert.binding')
    
    log.info('begin')
    
    convert_evidence(new_session_maker, 10000)    
    
    log.info('complete')
    
if __name__ == "__main__":
    from convert_all import new_config
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(new_session_maker, False)