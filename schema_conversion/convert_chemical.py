'''
Created on Jun 4, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection, cache_by_key, create_format_name
from sqlalchemy.orm import joinedload
import datetime
import model_new_schema
import model_old_schema


"""
------------ Create --------------
"""
def create_chemical(old_cv_term):
    from model_new_schema.chemical import Chemical as NewChemical
    
    display_name = old_cv_term.name
    format_name = create_format_name(display_name)
    source = 'EBI'
    
    new_chemical = NewChemical(display_name, format_name, source, 
                               old_cv_term.date_created, old_cv_term.created_by)
    return new_chemical

def create_alias(old_cv_term, key_to_chemical):
    from model_new_schema.chemical import ChemicalAlias as NewChemicalAlias
    
    chemical_key = create_format_name(old_cv_term.name)
    if chemical_key not in key_to_chemical:
        print 'Chemical does not exist.'
        return []
    chemical_id = key_to_chemical[chemical_key].id
    
    new_aliases = [NewChemicalAlias(synonym.synonym, 'EBI', chemical_id,
                        synonym.date_created, synonym.created_by) for synonym in old_cv_term.cv_synonyms]
    return new_aliases

def create_altids(old_cv_term, key_to_chemical):
    from model_new_schema.chemical import ChemicalAltid as NewChemicalAltid
    
    chemical_key = create_format_name(old_cv_term.name)
    if chemical_key not in key_to_chemical:
        print 'Chemical does not exist.'
        return []
    chemical_id = key_to_chemical[chemical_key].id
    
    new_altids = [NewChemicalAltid(dbxref.dbxref_id, 'EBI', 'CHEBI', chemical_id, 
                                   dbxref.date_created, dbxref.created_by) 
                  for dbxref in old_cv_term.dbxrefs]
    return new_altids

def create_chemrels(old_cv_term, key_to_chemical):
    from model_new_schema.chemical import ChemicalRelation as NewChemicalRelations
    
    child_chemical_key = create_format_name(old_cv_term.name)
    if child_chemical_key not in key_to_chemical:
        print 'Chemical does not exist.'
        return []
    child_id = key_to_chemical[child_chemical_key].id
    
    new_chemrels = []
    for parent_rel in old_cv_term.parent_rels:
        parent_chemical_key = create_format_name(parent_rel.parent.name)
        if parent_chemical_key not in key_to_chemical:
            print 'Chemical does not exist.'
        else:
            parent_id = key_to_chemical[parent_chemical_key].id
            new_chemrels.append(NewChemicalRelations(parent_rel.id, parent_id, child_id,
                                                 parent_rel.date_created, parent_rel.created_by))
    
    return new_chemrels
     
"""
---------------------Convert------------------------------
"""  

def convert(old_session_maker, new_session_maker):
    from model_old_schema.cv import CVTerm as OldCVTerm

#    # Convert chemicals
#    print 'Chemicals'
#    new_session = new_session_maker()
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==3).all()
#
#        success=False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_chemicals(new_session, old_cv_terms)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert aliases
#    print 'Aliases'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==3).options(joinedload('cv_synonyms')).all()
#
#        success=False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_aliases(new_session, old_cv_terms)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
#        
#    # Convert altids
#    print 'Altids'
#    start_time = datetime.datetime.now()
#    try:
#        old_session = old_session_maker()
#        old_cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==3).options(
#               joinedload('cv_dbxrefs'), joinedload('cv_dbxrefs.dbxref')).all()
#
#        success=False
#        while not success:
#            new_session = new_session_maker()
#            success = convert_altids(new_session, old_cv_terms)
#            ask_to_commit(new_session, start_time)  
#            new_session.close()
#    finally:
#        old_session.close()
#        new_session.close()
        
    # Convert ChemicalRelations
    print 'ChemicalRelations'
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        old_cv_terms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==3).options(
                joinedload('parent_rels'), joinedload('parent_rels.parent')).all()

        success=False
        while not success:
            new_session = new_session_maker()
            success = convert_chemicalrels(new_session, old_cv_terms)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
def convert_chemicals(new_session, old_cv_terms):
    '''
    Convert Chemicals
    '''
    from model_new_schema.chemical import Chemical as NewChemical
    
    #Cache chemicals
    key_to_chemical = cache_by_key(NewChemical, new_session)

    #Create new chemicals if they don't exist, or update the database if they do.
    new_chemicals = [create_chemical(x) for x in old_cv_terms]
    values_to_check = ['display_name', 'source', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_chemicals, key_to_chemical, values_to_check, new_session)
    return success

def convert_aliases(new_session, old_cv_terms):
    '''
    Convert Aliases
    '''
    from model_new_schema.chemical import Chemical as NewChemical, ChemicalAlias as NewChemicalAlias
    
    #Cache aliases
    key_to_alias = cache_by_key(NewChemicalAlias, new_session)
    key_to_chemical = cache_by_key(NewChemical, new_session)

    #Create new aliases if they don't exist, or update the database if they do.
    new_aliases = []
    for old_cv_term in old_cv_terms:
        new_aliases.extend(create_alias(old_cv_term, key_to_chemical))
    values_to_check = ['used_for_search', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_aliases, key_to_alias, values_to_check, new_session)
    return success

def convert_altids(new_session, old_cv_terms):
    '''
    Convert Altids
    '''
    from model_new_schema.chemical import Chemical as NewChemical, ChemicalAltid as NewChemicalAltid
    
    #Cache altids
    key_to_altid = cache_by_key(NewChemicalAltid, new_session)
    key_to_chemical = cache_by_key(NewChemical, new_session)

    #Create new altids if they don't exist, or update the database if they do.
    new_altids = []
    for old_cv_term in old_cv_terms:
        new_altids.extend(create_altids(old_cv_term, key_to_chemical))
        
    values_to_check = ['chemical_id', 'source', 'altid_name', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_altids, key_to_altid, values_to_check, new_session)
    return success

def convert_chemicalrels(new_session, old_cv_terms):
    '''
    Convert ChemicalRelations
    '''
    from model_new_schema.chemical import Chemical as NewChemical, ChemicalRelation as NewChemicalRelation
    
    #Cache altids
    key_to_chemrels = cache_by_key(NewChemicalRelation, new_session)
    key_to_chemical = cache_by_key(NewChemical, new_session)

    #Create new chemrels if they don't exist, or update the database if they do.
    new_chemrels = []
    for old_cv_term in old_cv_terms:
        new_chemrels.extend(create_chemrels(old_cv_term, key_to_chemical))
        
    values_to_check = ['date_created', 'created_by']
    success = create_or_update_and_remove(new_chemrels, key_to_chemrels, values_to_check, new_session)
    return success

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)
    

