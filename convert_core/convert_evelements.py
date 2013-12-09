'''
Created on Jun 4, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, create_format_name, break_up_file, \
    read_obo
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10

"""
--------------------- Convert Experiment ---------------------
"""

def create_experiment(old_cv_term, key_to_source):
    from model_new_schema.evelements import Experiment as NewExperiment
    
    display_name = old_cv_term.name
    description = old_cv_term.definition
    
    source = key_to_source['SGD']
    new_experiment = NewExperiment(display_name, source, description, None,
                               old_cv_term.date_created, old_cv_term.created_by)
    return [new_experiment]

def create_experiment_from_reg_row(display_name, eco_id, source_key, key_to_source):
    from model_new_schema.evelements import Experiment
    
    if display_name is None:
        display_name = eco_id

    source = None if source_key.strip() not in key_to_source else key_to_source[source_key.strip()]
    new_experiment = Experiment(display_name, source, None, eco_id, None, None)
    return [new_experiment]

def create_experiment_from_binding_row(display_name, key_to_source):
    from model_new_schema.evelements import Experiment

    source = key_to_source['YeTFaSCo']
    new_experiment = Experiment(display_name,source, None, None, None, None)
    return [new_experiment]

def create_experiment_from_eco(eco_term, key_to_source):
    from model_new_schema.evelements import Experiment
    source = key_to_source['ECO']
    new_experiment = Experiment(eco_term['name'], source, None if 'def' not in eco_term else eco_term['def'], eco_term['id'], None, None)
    return [new_experiment]

def convert_experiment(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Experiment as NewExperiment, Source as NewSource
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
        values_to_check = ['display_name', 'link', 'description', 'eco_id', 'source_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        already_seen_objs = set()
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).all()
        
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        for old_obj in read_obo('data/eco.obo'):
            #Convert old objects into new ones
            newly_created_objs = create_experiment_from_eco(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen_objs:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen_objs.add(newly_created_obj.unique_key())
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen_objs:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen_objs.add(newly_created_obj.unique_key())
                       
        #Get experiments from regulation files
        experiment_names = set()
        
        rows = break_up_file('data/yeastmine_regulation.tsv')
        experiment_names.update([(row[4], row[5], row[11]) for row in rows])
                
        for experiment_name, eco_id, source_key in experiment_names:
            newly_created_objs = create_experiment_from_reg_row(experiment_name, eco_id, source_key, key_to_source)
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen_objs:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)    
                    already_seen_objs.add(newly_created_obj.unique_key())                    
          
        experiment_names = set()      
        #Add experiments from binding files
        rows = break_up_file('data/yetfasco_data.txt', delimeter=';')
        for row in rows:
            if len(row) < 10:
                print row
        experiment_names.update([row[9][1:-1] for row in rows])
        
        for experiment_name in experiment_names:
            newly_created_objs = create_experiment_from_binding_row(experiment_name, key_to_source)
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen_objs:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)   
                    already_seen_objs.add(newly_created_obj.unique_key())                      
                        
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
    
def create_experiment_alias(old_cv_term, key_to_experiment, key_to_source):
    from model_new_schema.evelements import Experimentalias as NewExperimentalias
    
    experiment_key = create_format_name(old_cv_term.name)
    if experiment_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return None
    experiment = key_to_experiment[experiment_key]
    source = key_to_source['SGD']
    
    new_altids = [NewExperimentalias(dbxref.dbxref_id, source, 'APOID', experiment,
                                   dbxref.date_created, dbxref.created_by) 
                  for dbxref in old_cv_term.dbxrefs]
    return new_altids

def convert_experiment_alias(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Experiment as NewExperiment, Source as NewSource, Experimentalias as NewExperimentalias
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
        values_to_check = ['source_id', 'category']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('cv_dbxrefs'), 
                                                    joinedload('cv_dbxrefs.dbxref')).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment_alias(old_obj, key_to_experiment, key_to_source)
                
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

def create_experiment_relation(old_cv_term, key_to_experiment, key_to_source):
    from model_new_schema.evelements import Experimentrelation as NewExperimentrelation
    
    source = key_to_source['SGD']
    
    child_key = create_format_name(old_cv_term.name)
    if child_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return None
    child = key_to_experiment[child_key]
    
    new_rels = []
    for parent_rel in old_cv_term.parent_rels:
        parent_key = create_format_name(parent_rel.parent.name)
        if parent_key not in key_to_experiment:
            print 'Experiment does not exist.'
        else:
            parent = key_to_experiment[parent_key]
            new_rels.append(NewExperimentrelation(source, None, parent, child,
                                                 parent_rel.date_created, parent_rel.created_by))
    
    return new_rels

def convert_experiment_relation(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Experiment as NewExperiment, Experimentrelation as NewExperimentrelation, Source as NewSource
    from model_old_schema.cv import CVTerm as OldCVTerm
    
    log = logging.getLogger('convert.evelements.experiment_relation')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewExperimentrelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = []
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('parent_rels'), 
                                                    joinedload('parent_rels.parent')).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment_relation(old_obj, key_to_experiment, key_to_source)
                
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

def create_strain(old_cv_term, key_to_source):
    from model_new_schema.evelements import Strain as NewStrain
    
    display_name = old_cv_term.name
    description = old_cv_term.definition
    
    source = key_to_source['SGD']
    
    new_strain = NewStrain(display_name, source, description,
                               old_cv_term.date_created, old_cv_term.created_by)
    return [new_strain]

def convert_strain(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Strain as NewStrain, Source as NewSource
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
        values_to_check = ['display_name', 'link', 'description']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==10).all()
        
        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_strain(old_obj, key_to_source)
                
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
--------------------- Convert Source ---------------------
"""
sources = ['SGD', 'GO', 'PROSITE', 'Gene3D', 'SUPERFAMILY', 'TIGRFAMs', 'Pfam', 'PRINTS', 
               'PIR superfamily', 'JASPAR', 'SMART', 'PANTHER', 'ProDom', 'DOI', 'PubMedCentral', 'PubMed', '-', 'ECO']

def create_extra_source():
    from model_new_schema.evelements import Source as NewSource
    new_sources = []
    for display_name in sources:        
        new_sources.append(NewSource(display_name, None, None, None))
    return new_sources

ok_codes = set([('ALIAS', 'ALIAS_TYPE'), ('DBXREF', 'SOURCE'), ('EXPERIMENT', 'SOURCE'), ('FEATURE', 'SOURCE'),
                ('GO_ANNOTATION', 'SOURCE'), ('HOMOLOG', 'SOURCE'), ('INTERACTION', 'SOURCE'), ('PHENOTYPE', 'SOURCE'),
                ('REFTYPE', 'SOURCE'), ('REFERENCE', 'SOURCE'), ('URL', 'SOURCE')])

def create_source_from_code(code):
    from model_new_schema.evelements import Source as NewSource
    
    if (code.tab_name, code.col_name) in ok_codes:
        display_name = code.code_value        
        new_source = NewSource(display_name, code.description, code.date_created, code.created_by)
        return [new_source]
    return []

def convert_source(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.cv import Code as OldCode
    
    log = logging.getLogger('convert.evelements.source')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewSource).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'description']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set();
        
        #Create basic sources
        newly_created_objs = create_extra_source()
            
        #Edit or add new objects
        for newly_created_obj in newly_created_objs:
            if newly_created_obj.unique_key() not in already_seen:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
                already_seen.add(newly_created_obj.unique_key())
            
        #Create sources from code table  
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCode).all()
                 
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_source_from_code(old_obj)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen.add(newly_created_obj.unique_key())
                                                
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
    convert_source(old_session_maker, new_session_maker)
    
    convert_experiment(old_session_maker, new_session_maker)
    
    convert_experiment_alias(old_session_maker, new_session_maker)
    
    convert_experiment_relation(old_session_maker, new_session_maker)
    
    convert_strain(old_session_maker, new_session_maker)


    

