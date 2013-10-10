'''
Created on Jun 4, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, prepare_schema_connection, create_format_name, break_up_file
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
from convert_utils.link_maker import experiment_link, strain_link
import logging
import model_new_schema
import model_old_schema
import sys

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10

"""
--------------------- Convert Experiment ---------------------
"""
    
def create_experiment_id(old_cv_term_id):
    return old_cv_term_id

def create_experiment_id_from_reg_row(old_experiment_id, format_name):
    if format_name == 'chromatin_immunoprecipitation-chip_evidence':
        return 700000
    else:
        return old_experiment_id + 700001
    
def create_experiment_id_from_binding_row(old_experiment_id, format_name):
    return old_experiment_id + 900000

def create_experiment(old_cv_term):
    from model_new_schema.evelement import Experiment as NewExperiment
    
    display_name = old_cv_term.name
    format_name = create_format_name(display_name)
    description = old_cv_term.definition
    link = experiment_link(format_name)
    
    new_experiment = NewExperiment(create_experiment_id(old_cv_term.id), display_name, format_name, link, description, None,
                               old_cv_term.date_created, old_cv_term.created_by)
    return [new_experiment]

def create_experiment_from_reg_row(display_name, eco_id, row_id):
    from model_new_schema.evelement import Experiment
    
    if display_name is None:
        display_name = eco_id
    format_name = create_format_name(display_name)
    
    if display_name.endswith('evidence'):
        display_name = display_name[:-9]
        
    link = experiment_link(format_name)

    new_experiment = Experiment(create_experiment_id_from_reg_row(row_id, format_name), display_name, format_name, link, None, eco_id, None, None)
    return [new_experiment]

def create_experiment_from_binding_row(display_name, row_id):
    from model_new_schema.evelement import Experiment
    
    format_name = create_format_name(display_name)
    link = experiment_link(format_name)

    new_experiment = Experiment(create_experiment_id_from_binding_row(row_id, format_name), display_name, format_name, link, None, None, None, None)
    return [new_experiment]

def convert_experiment(old_session_maker, new_session_maker):
    from model_new_schema.evelement import Experiment as NewExperiment
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    log = logging.getLogger('convert.evelements.experiment')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewExperiment).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'link', 'description', 'date_created', 'created_by', 'eco_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment(old_obj)
                
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
                       
        #Get experiments from regulation files
        experiment_names = set()
        
        rows = break_up_file('/Users/kpaskov/final/yeastmine_regulation.tsv')
        experiment_names.update([(row[4], row[5]) for row in rows])
                
        i=0
        for experiment_name, eco_id in experiment_names:
            newly_created_objs = create_experiment_from_reg_row(experiment_name, eco_id, i)
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)                        
                i = i+1
          
        experiment_names = set()      
        #Add experiments from binding files
        rows = break_up_file('/Users/kpaskov/final/yetfasco_data.txt', delimeter=';')
        for row in rows:
            if len(row) < 10:
                print row
        experiment_names.update([row[9][1:-1] for row in rows])
        
        i=0
        for experiment_name in experiment_names:
            newly_created_objs = create_experiment_from_binding_row(experiment_name, i)
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)                        
                i = i+1
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            print 'Removed at end'
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
--------------------- Convert Experiment Alias ---------------------
"""
    
def create_experiment_alias(old_cv_term, key_to_experiment):
    from model_new_schema.evelement import Experimentalias as NewExperimentalias
    
    experiment_key = create_format_name(old_cv_term.name)
    if experiment_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return None
    experiment_id = key_to_experiment[experiment_key].id
    
    new_altids = [NewExperimentalias(dbxref.dbxref_id, 'SGD', 'APOID', experiment_id, 
                                   dbxref.date_created, dbxref.created_by) 
                  for dbxref in old_cv_term.dbxrefs]
    return new_altids

def convert_experiment_alias(old_session_maker, new_session_maker):
    from model_new_schema.evelement import Experiment as NewExperiment, Experimentalias as NewExperimentalias
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    log = logging.getLogger('convert.evelements.experiment_alias')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewExperimentalias).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['source', 'category', 'date_created', 'created_by']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('cv_dbxrefs'), 
                                                    joinedload('cv_dbxrefs.dbxref')).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment_alias(old_obj, key_to_experiment)
                
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
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Experiment Relation ---------------------
"""

def create_experiment_relation_id(parent_rel_id):
    return parent_rel_id
    
def create_experiment_relation(old_cv_term, key_to_experiment):
    from model_new_schema.evelement import ExperimentRelation as NewExperimentRelation
    
    child_key = create_format_name(old_cv_term.name)
    if child_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return None
    child_id = key_to_experiment[child_key].id
    
    new_rels = []
    for parent_rel in old_cv_term.parent_rels:
        parent_key = create_format_name(parent_rel.parent.name)
        if parent_key not in key_to_experiment:
            print 'Experiment does not exist.'
        else:
            parent_id = key_to_experiment[parent_key].id
            new_rels.append(NewExperimentRelation(create_experiment_relation_id(parent_rel.id), parent_id, child_id,
                                                 parent_rel.date_created, parent_rel.created_by))
    
    return new_rels

def convert_experiment_relation(old_session_maker, new_session_maker):
    from model_new_schema.evelement import Experiment as NewExperiment, ExperimentRelation as NewExperimentRelation
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    log = logging.getLogger('convert.evelements.experiment_relation')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewExperimentRelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['date_created', 'created_by']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('parent_rels'), 
                                                    joinedload('parent_rels.parent')).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment_relation(old_obj, key_to_experiment)
                
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
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')
    
"""
--------------------- Convert Strain ---------------------
"""
strain_id_map = {67178:1, 67179:21, 
                 67180:22, 67181:8, 
                 67182:2, 67183:23, 
                 67184:24, 67185:25, 
                 67186:26, 175301:27, 
                 214704:28, 214705:29, 
                 214706:30}
def create_strain_id(old_cv_term_id):
    return strain_id_map[old_cv_term_id]

def create_strain(old_cv_term):
    from model_new_schema.evelement import Strain as NewStrain
    
    display_name = old_cv_term.name
    format_name = create_format_name(display_name)
    description = old_cv_term.definition
    link = strain_link(format_name)
    
    new_strain = NewStrain(create_strain_id(old_cv_term.id), display_name, format_name, link, description,
                               old_cv_term.date_created, old_cv_term.created_by)
    return [new_strain]

def convert_strain(old_session_maker, new_session_maker):
    from model_new_schema.evelement import Strain as NewStrain
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    log = logging.getLogger('convert.evelements.strain')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewStrain).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'link', 'description', 'date_created', 'created_by']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==10).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_strain(old_obj)
                
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
        output_creator.finished()
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
    log = set_up_logging('convert.evelements')
    
    log.info('begin')
    
    convert_experiment(old_session_maker, new_session_maker)
    
    convert_experiment_alias(old_session_maker, new_session_maker)
    
    convert_experiment_relation(old_session_maker, new_session_maker)
    
    convert_strain(old_session_maker, new_session_maker)

    log.info('complete')

if __name__ == "__main__":
    from convert_all import new_config, old_config
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)
    

