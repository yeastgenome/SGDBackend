import logging
import sys

from sqlalchemy.sql.expression import or_

from src.sgd.convert import OutputCreator, create_or_update


__author__ = 'kpaskov'

#1.23.14 Maitenance (sgd-dev): :19

# --------------------- Convert Chemical ---------------------
def create_chemical(expt_property, key_to_source):
    from src.sgd.model.nex.chemical import Chemical as NewChemical

    display_name = expt_property.value
    source = key_to_source['SGD']
    new_chemical = NewChemical(display_name, source, None, None, expt_property.date_created, expt_property.created_by)
    return [new_chemical]

def create_chemical_from_cv_term(old_cvterm, key_to_source):
    from src.sgd.model.nex.chemical import Chemical as NewChemical
    source = key_to_source['SGD']
    new_chemical = NewChemical(old_cvterm.name, source, old_cvterm.dbxref_id,
                               old_cvterm.definition, old_cvterm.date_created, old_cvterm.created_by)
    return [new_chemical]

def convert_chemical(old_session_maker, new_session_maker):
    from src.sgd.model.nex.chemical import Chemical as NewChemical
    from src.sgd.model.nex.evelements import Source as NewSource
    from src.sgd.model.bud.phenotype import ExperimentProperty as OldExperimentProperty
    from src.sgd.model.bud.cv import CVTerm as OldCVTerm

    new_session = None
    old_session = None
    log = logging.getLogger('convert.chemical.chemical')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     
        
        #Grab all current objects
        current_objs = new_session.query(NewChemical).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['source_id', 'link', 'display_name', 'chebi_id']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        keys_already_seen = set()
            
        #Grab old objects
        old_objs = old_session.query(OldExperimentProperty).filter(or_(OldExperimentProperty.type=='Chemical_pending', 
                                                                       OldExperimentProperty.type == 'chebi_ontology')).all()
                                                                       
        #Grab cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
         
        old_cvterms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no == 3).all()           
        #Convert cv terms           
        for old_obj in old_cvterms:
            #Convert old objects into new ones
            newly_created_objs = create_chemical_from_cv_term(old_obj, key_to_source)
                
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

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_chemical(old_obj, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
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
        
# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):
    convert_chemical(old_session_maker, new_session_maker)