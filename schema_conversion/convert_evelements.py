'''
Created on Jun 4, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, \
    prepare_schema_connection, cache_by_key, create_format_name, create_or_update, \
    execute_conversion
from sqlalchemy.orm import joinedload
import model_new_schema
import model_old_schema


"""
------------ Create --------------
"""
def create_experiment(old_cv_term):
    from model_new_schema.evelement import Experiment as NewExperiment
    
    display_name = old_cv_term.name
    format_name = create_format_name(display_name)
    description = old_cv_term.definition
    
    new_experiment = NewExperiment(old_cv_term.id, display_name, format_name, description,
                               old_cv_term.date_created, old_cv_term.created_by)
    return new_experiment

def create_experiment_altids(old_cv_term, key_to_experiment):
    from model_new_schema.evelement import ExperimentAltid as NewExperimentAltid
    
    experiment_key = create_format_name(old_cv_term.name)
    if experiment_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return []
    experiment_id = key_to_experiment[experiment_key].id
    
    new_altids = [NewExperimentAltid(dbxref.dbxref_id, 'SGD', 'APOID', experiment_id, 
                                   dbxref.date_created, dbxref.created_by) 
                  for dbxref in old_cv_term.dbxrefs]
    return new_altids

def create_experiment_rels(old_cv_term, key_to_experiment):
    from model_new_schema.evelement import ExperimentRelation as NewExperimentRelation
    
    child_key = create_format_name(old_cv_term.name)
    if child_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return []
    child_id = key_to_experiment[child_key].id
    
    new_rels = []
    for parent_rel in old_cv_term.parent_rels:
        parent_key = create_format_name(parent_rel.parent.name)
        if parent_key not in key_to_experiment:
            print 'Experiment does not exist.'
        else:
            parent_id = key_to_experiment[parent_key].id
            new_rels.append(NewExperimentRelation(parent_rel.id, parent_id, child_id,
                                                 parent_rel.date_created, parent_rel.created_by))
    
    return new_rels

def create_strain(old_cv_term):
    from model_new_schema.evelement import Strain as NewStrain
    
    display_name = old_cv_term.name
    format_name = create_format_name(display_name)
    description = old_cv_term.definition
    
    new_strain = NewStrain(old_cv_term.id, display_name, format_name, description,
                               old_cv_term.date_created, old_cv_term.created_by)
    return new_strain
     
"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker, ask=True):
    from model_old_schema.cv import CVTerm as OldCVTerm

    # Convert experiments
    print 'Experiment'
    execute_conversion(convert_experiments, old_session_maker, new_session_maker, ask,
                       old_cv_terms=lambda old_session: old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).all())
    
        
    # Convert experiment altids
    print 'Experiment Altid'
    execute_conversion(convert_experiment_altids, old_session_maker, new_session_maker, ask,
                       old_cv_terms=lambda old_session: old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('cv_dbxrefs'), 
                                                    joinedload('cv_dbxrefs.dbxref')).all())

    # Convert experiment relations
    print 'ExperimentRelation'
    execute_conversion(convert_experiment_rels, old_session_maker, new_session_maker, ask,
                       old_cv_terms=lambda old_session: old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('parent_rels'), 
                                                    joinedload('parent_rels.parent'), ).all())
        
    # Convert strains
    print 'Strain'
    execute_conversion(convert_strains, old_session_maker, new_session_maker, ask,
                       old_cv_terms=lambda old_session: old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).all())

        
def convert_experiments(new_session, old_cv_terms=None):
    '''
    Convert Experiments
    '''
    from model_new_schema.evelement import Experiment as NewExperiment
    
    #Cache experiments
    key_to_experiment = cache_by_key(NewExperiment, new_session)

    #Create new experiments if they don't exist, or update the database if they do.
    new_experiments = [create_experiment(x) for x in old_cv_terms]
    values_to_check = ['display_name', 'description', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_experiments, key_to_experiment, values_to_check, new_session)
    return success

def convert_experiment_altids(new_session, old_cv_terms=None):
    '''
    Convert Experiment Altids
    '''
    from model_new_schema.evelement import Experiment as NewExperiment, ExperimentAltid as NewExperimentAltid
    
    #Cache altids
    key_to_altid = cache_by_key(NewExperimentAltid, new_session)
    key_to_experiment = cache_by_key(NewExperiment, new_session)

    #Create new altids if they don't exist, or update the database if they do.
    new_altids = []
    for old_cv_term in old_cv_terms:
        new_altids.extend(create_experiment_altids(old_cv_term, key_to_experiment))
        
    values_to_check = ['experiment_id', 'source', 'altid_name', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_altids, key_to_altid, values_to_check, new_session)
    return success

def convert_experiment_rels(new_session, old_cv_terms=None):
    '''
    Convert ExperimentRelations
    '''
    from model_new_schema.evelement import Experiment as NewExperiment, ExperimentRelation as NewExperimentRelation
    
    #Cache altids
    key_to_rels = cache_by_key(NewExperimentRelation, new_session)
    key_to_experiment = cache_by_key(NewExperiment, new_session)

    #Create new relations if they don't exist, or update the database if they do.
    new_rels = []
    for old_cv_term in old_cv_terms:
        new_rels.extend(create_experiment_rels(old_cv_term, key_to_experiment))
        
    values_to_check = ['date_created', 'created_by']
    success = create_or_update_and_remove(new_rels, key_to_rels, values_to_check, new_session)
    return success

def convert_strains(new_session, old_cv_terms=None):
    '''
    Convert Strains
    '''
    from model_new_schema.evelement import Strain as NewStrain
    
    #Cache straings
    key_to_strain = cache_by_key(NewStrain, new_session)

    #Create new experiments if they don't exist, or update the database if they do.
    new_strains = [create_strain(x) for x in old_cv_terms]
    values_to_check = ['display_name', 'description', 'date_created', 'created_by']
    success = create_or_update(new_strains, key_to_strain, values_to_check, new_session)
    return success

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)
    

