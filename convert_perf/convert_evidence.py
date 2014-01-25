'''
Created on Oct 29, 2013

@author: kpaskov
'''
import json
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
import logging
import sys


"""
--------------------- Convert Evidence ---------------------
"""

def create_evidence(obj_id, json_obj):
    from model_perf_schema.evidence import Evidence
    if json_obj is not None:
        return Evidence(obj_id, json_obj)
    else:
        return None

def create_bioentity_evidence(bioentity_id, class_type, evidence_id):
    from model_perf_schema.evidence import BioentityEvidence
    return BioentityEvidence(bioentity_id, class_type, evidence_id)

def update_evidence(json_obj, old_obj):
    changed = False
    if json_obj is not None and old_obj.json != json_obj:
        old_obj.json = json_obj
        changed = True
    return changed

def convert_evidence(session_maker, class_type, new_obj_f, label, obj_ids, chunk_size, check_known_evidence):
    from model_perf_schema.evidence import Evidence, BioentityEvidence
    log = logging.getLogger(label)
    log.info('begin')
    output_creator = OutputCreator(log)
    evidence_output_creator = OutputCreator(log)
    
    try:
        session = session_maker()
        
        num_chunks = ceil(1.0*len(obj_ids)/chunk_size)
        for i in range(0, num_chunks):
            chunk_obj_ids = obj_ids[i*chunk_size: (i+1)*chunk_size]
            
            #Grab old objects and current_objs
            old_objs = session.query(BioentityEvidence).filter(BioentityEvidence.class_type == class_type).filter(BioentityEvidence.bioentity_id.in_(chunk_obj_ids)).all()

            new_tuples = set()
            id_to_evidence = {}

            for x in chunk_obj_ids:
                y_json = json.loads(new_obj_f(x))
                new_tuples.update((x, evidence['id']) for evidence in y_json)
                id_to_evidence.update([(evidence['id'], json.dumps(evidence)) for evidence in y_json])

            evidence_ids = id_to_evidence.keys()
            old_id_to_evidence = {}
            num_ev_chunks = ceil(1.0*len(evidence_ids)/500)
            for j in range(num_ev_chunks):
                old_id_to_evidence.update([(x.id, x) for x in session.query(Evidence).filter(Evidence.id.in_(evidence_ids[j*500:(j+1)*500])).all()])

            for evidence_id, evidence_json in id_to_evidence.iteritems():
                if evidence_id not in old_id_to_evidence:
                    new_evidence = create_evidence(evidence_id, evidence_json)
                    if new_evidence is not None:
                        session.add(new_evidence)
                        evidence_output_creator.added()
                elif check_known_evidence:
                    if update_evidence(evidence_json, old_id_to_evidence[evidence_id]):
                        evidence_output_creator.changed(evidence_id, 'json')
            evidence_output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()

            old_tuple_to_obj = dict([((x.bioentity_id, x.evidence_id), x) for x in old_objs])
            
            old_tuples = set(old_tuple_to_obj.keys())

            #Inserts
            insert_tuples = new_tuples - old_tuples
            for insert_tuple in insert_tuples:
                new_obj = create_bioentity_evidence(insert_tuple[0], class_type, insert_tuple[1])
                if new_obj is not None:
                    session.add(new_obj)
                    output_creator.added()
                
            #Deletes
            delete_tuples = old_tuples - new_tuples
            for delete_tuple in delete_tuples:
                session.delete(old_tuple_to_obj[delete_tuple])
            output_creator.num_removed = output_creator.num_removed + len(delete_tuples)
            
        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            session.commit()
        
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        session.close()
        
    log.info('complete')