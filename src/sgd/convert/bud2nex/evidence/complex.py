import logging
import sys

from src.sgd.convert import OutputCreator, create_or_update


__author__ = 'kpaskov'

# --------------------- Convert Evidence ---------------------
def create_evidence(complex, id_to_go, id_to_bioentity, go_id_to_bioent_ids, key_to_source):
    from src.sgd.model.nex.evidence import Complexevidence

    source = key_to_source['GO']
    evidences = []
    if complex.go_id in go_id_to_bioent_ids:
        go = id_to_go[complex.go_id]
        for bioent_id in go_id_to_bioent_ids[complex.go_id]:
            bioentity = id_to_bioentity[bioent_id]
            evidences.append(Complexevidence(source, bioentity, complex, go, None, None))
    return evidences

def convert_evidence(new_session_maker):
    from src.sgd.model.nex.evidence import Complexevidence, Goevidence
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity, Complex
    from src.sgd.model.nex.bioconcept import Go

    new_session = None
    log = logging.getLogger('convert.complex.evidence')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = []
        
        #Grab cached dictionaries
        id_to_go = dict([(x.id, x) for x in new_session.query(Go).all()])
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(Bioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        
        #Grab old objects
        complexes = new_session.query(Complex).all()

        go_id_to_bioent_ids = dict([(x.go_id, set()) for x in complexes])
        for goevidence in new_session.query(Goevidence).filter(Goevidence.bioconcept_id.in_([x.go_id for x in complexes])).filter(Goevidence.qualifier != 'colocalizes with').filter(Goevidence.annotation_type != 'computational'):
            go_id_to_bioent_ids[goevidence.bioconcept_id].add(goevidence.bioentity_id)
        
        current_objs = new_session.query(Complexevidence).filter(Complexevidence.go_id != None).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
        untouched_obj_ids = set(id_to_current_obj.keys())

        for old_obj in complexes:
            #Convert old objects into new ones
            newly_created_objs = create_evidence(old_obj, id_to_go, id_to_bioentity, go_id_to_bioent_ids, key_to_source)
     
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

# --------------------- Convert Biofact ---------------------
def create_biofact(complex, id_to_go, complex_id_to_bioent_ids, bioent_id_to_go_ids):
    from src.sgd.model.nex.auxiliary import Biofact

    biofacts = []

    go_id_to_bioent_ids = {}
    if complex.id in complex_id_to_bioent_ids:
        for bioent_id in complex_id_to_bioent_ids[complex.id]:
            if bioent_id in bioent_id_to_go_ids:
                for go_id in bioent_id_to_go_ids[bioent_id]:
                    if go_id in go_id_to_bioent_ids:
                        go_id_to_bioent_ids[go_id].add(bioent_id)
                    else:
                        go_id_to_bioent_ids[go_id] = {bioent_id}

    for go_id, bioent_ids in go_id_to_bioent_ids.iteritems():
        if len(bioent_ids) > 1:
            biofacts.append(Biofact(complex, id_to_go[go_id]))
    return biofacts

def convert_biofact(new_session_maker):
    from src.sgd.model.nex.evidence import Complexevidence
    from src.sgd.model.nex.bioentity import Complex
    from src.sgd.model.nex.bioconcept import Go
    from src.sgd.model.nex.auxiliary import Biofact

    new_session = None
    log = logging.getLogger('convert.complex.biofact')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = []

        #Grab cached dictionaries
        id_to_go = dict([(x.id, x) for x in new_session.query(Go).all()])

        #Grab old objects
        complexes = new_session.query(Complex).all()

        complex_id_to_bioent_ids = {}
        for evidence in new_session.query(Complexevidence):
            if evidence.complex_id in complex_id_to_bioent_ids:
                complex_id_to_bioent_ids[evidence.complex_id].add(evidence.bioentity_id)
            else:
                complex_id_to_bioent_ids[evidence.complex_id] = {evidence.bioentity_id}

        bioent_id_to_go_ids = {}
        for biofact in new_session.query(Biofact).filter(Biofact.bioentity_class_type == 'LOCUS').filter(Biofact.bioconcept_class_type == 'GO'):
            if biofact.bioentity_id in bioent_id_to_go_ids:
                bioent_id_to_go_ids[biofact.bioentity_id].add(biofact.bioconcept_id)
            else:
                bioent_id_to_go_ids[biofact.bioentity_id] = {biofact.bioconcept_id}

        current_objs = new_session.query(Biofact).filter(Biofact.bioentity_class_type == 'COMPLEX').filter(Biofact.bioconcept_class_type == 'GO').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        for old_obj in complexes:
            #Convert old objects into new ones
            newly_created_objs = create_biofact(old_obj, id_to_go, complex_id_to_bioent_ids, bioent_id_to_go_ids)

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
    convert_evidence(new_session_maker)

    convert_biofact(new_session_maker)
