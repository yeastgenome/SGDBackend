import logging
import sys

from sqlalchemy.orm import joinedload

from src.sgd.convert import OutputCreator, create_or_update


__author__ = 'kpaskov'

# --------------------- Convert Evidence ---------------------
def create_evidence(old_dbxref, id_to_bioentity, key_to_bioentity, key_to_source, key_to_bioconcept):
    from src.sgd.model.nex.evidence import ECNumberevidence
    evidences = []

    source = key_to_source[old_dbxref.source]
    bioconcept_key = (old_dbxref.dbxref_id, 'EC_NUMBER')
    bioconcept = None if bioconcept_key not in key_to_bioconcept else key_to_bioconcept[bioconcept_key]
    if bioconcept is None:
        print 'Bioconcept not found: ' + str(bioconcept_key)
        return []

    for dbxref_feat in old_dbxref.dbxref_feats:
        protein_key = (id_to_bioentity[dbxref_feat.feature_id].format_name + 'P', 'PROTEIN')
        protein = None if protein_key not in key_to_bioentity else key_to_bioentity[protein_key]
        if protein is None:
            print 'Bioentity not found: ' + str(protein_key)
        else:
            evidences.append(ECNumberevidence(source, protein, bioconcept, old_dbxref.date_created, old_dbxref.created_by))

    return evidences

def convert_evidence(old_session_maker, new_session_maker):
    from src.sgd.model.nex.evidence import ECNumberevidence as NewECNumberevidence
    from src.sgd.model.nex.bioentity import Locus as NewLocus, Protein as NewProtein
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.nex.bioconcept import ECNumber as NewECNumber
    from src.sgd.model.bud.general import Dbxref as OldDbxref

    new_session = None
    old_session = None
    log = logging.getLogger('convert.ec_number.evidence')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['source_id', 'bioentity_id', 'bioconcept_id']
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewLocus).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(NewProtein).all()])
        key_to_bioconcept = dict([(x.unique_key(), x) for x in new_session.query(NewECNumber).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
                
        #Grab all current objects and old objects
        current_objs = new_session.query(NewECNumberevidence).all()
        old_objs = old_session.query(OldDbxref).filter(OldDbxref.dbxref_type == 'EC number').options(joinedload(OldDbxref.dbxref_feats)).all()

        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen_obj = set()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_evidence(old_obj, id_to_bioentity, key_to_bioentity, key_to_source, key_to_bioconcept)
                    
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
                    print 'Duplicate evidence: ' + str(obj_key)
                            
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

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):

    convert_evidence(old_session_maker, new_session_maker)

    #from src.sgd.model.nex.bioconcept import ECNumber
    #from src.sgd.model.nex.evidence import ECNumberevidence
    #convert_biofact(new_session_maker, ECNumberevidence, ECNumber, 'EC_NUMBER', 'convert.ec_number.biofact', 10000)