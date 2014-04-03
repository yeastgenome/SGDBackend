from math import ceil
import logging
import sys

from src.sgd.convert import OutputCreator, break_up_file, create_or_update


__author__ = 'kpaskov'

# --------------------- Convert Phosphorylation Evidence ---------------------
kinase_reference_id_to_num_annotations = {}
kinase_references_not_in_db = set()
def create_phosphorylation_evidence(row, key_to_source, key_to_bioentity):
    from src.sgd.model.nex.evidence import Phosphorylationevidence, Generalcondition, Bioentitycondition
    source = key_to_source['PhosphoGRID']
    if len(row) == 19:
        bioentity_key = (row[0], 'LOCUS')
        bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]
        if bioentity is None:
            return []

        site_index = int(row[2][1:])
        site_residue = row[2][0]

        experiment = None

        conditions = []

        site_functions = row[7]
        if site_functions != '-':
            for site_function in site_functions.split('|'):
                conditions.append(Generalcondition(site_function))

        kinases = row[9]
        if kinases != '-':
            for kinase in kinases.split('|'):
                bioent_key = (kinase, 'LOCUS')
                bioent = None if bioent_key not in key_to_bioentity else key_to_bioentity[bioent_key]
                if bioent is not None:
                    conditions.append(Bioentitycondition(None, 'Kinase', bioent))

        return [Phosphorylationevidence(source, None, experiment, bioentity, site_index, site_residue, conditions, None, None)]

    return []

def convert_phosphorylation_evidence(new_session_maker, chunk_size):
    from src.sgd.model.nex.evidence import Phosphorylationevidence
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity

    new_session = None
    log = logging.getLogger('convert.phosphorylation.evidence')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['site_residue', 'site_index', 'bioentity_id']

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])

        #Grab current objects
        current_objs = new_session.query(Phosphorylationevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        old_objs = break_up_file('src/sgd/convert/data/phosphosites.txt')

        num_chunks = int(ceil(1.0*len(old_objs)/chunk_size))
        for i in range(0, num_chunks):
            min_id = i*chunk_size
            max_id = (i+1)*chunk_size

            for old_obj in old_objs[min_id:max_id]:
                #Convert old objects into new ones
                newly_created_objs = create_phosphorylation_evidence(old_obj, key_to_source, key_to_bioentity)

                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        if unique_key not in already_seen:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)
                            already_seen.add(unique_key)

            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()

        print kinase_reference_id_to_num_annotations
        print kinase_references_not_in_db

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

# ---------------------Convert------------------------------
def convert(new_session_maker):

    convert_phosphorylation_evidence(new_session_maker, 1000)