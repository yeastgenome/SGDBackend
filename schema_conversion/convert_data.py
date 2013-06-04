'''
Created on May 31, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, ask_to_commit, \
    prepare_schema_connection, cache_by_key, cache_by_id
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
import datetime
import model_new_schema
import model_old_schema


"""
---------------------Create------------------------------
"""


"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):
    from model_old_schema.reference import LitguideFeat as OldLitguideFeat
    from model_old_schema.feature import Feature as OldFeature
    
    # Convert Bioentity
    print 'Bioentity'
    start_time = datetime.datetime.now()
    new_session = new_session_maker()
    try:
        old_session = old_session_maker()
        old_bioentity = old_session.query(OldFeature).options(joinedload('annotation')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_bioentities(new_session, old_bioentity)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
    
    # Convert Bioentevidence
    print 'Bioentevidence'
    start_time = datetime.datetime.now()
    new_session = new_session_maker()
    try:
        old_session = old_session_maker()
        old_bioentevidence = old_session.query(OldLitguideFeat).filter(
                            or_(OldLitguideFeat.topic=='Additional Literature',
                                OldLitguideFeat.topic=='Primary Literature',
                                OldLitguideFeat.topic=='Omics',
                                OldLitguideFeat.topic=='Reviews')).options(joinedload('litguide')).all()

        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_bioentevidence(new_session, old_bioentevidence)
            ask_to_commit(new_session, start_time)  
            new_session.close()
    finally:
        old_session.close()
        new_session.close()
        
def convert_bioentities(new_session, old_bioentity):
    
    from model_new_schema.bioentity import Gene as NewGene
    
    #Cache bioentities
    key_to_bioentity = cache_by_key(NewGene, new_session)
    
    #Create new genes if they don't exist, or update the database if they do. 
    new_bioentities = [create_bioentity(x) for x in old_bioentity]
    
    values_to_check = ['display_name', 'dbxref_id', 'source', 'status', 'date_created', 'created_by',
                       'qualifier', 'attribute', 'name_description', 'headline', 'description', 'genetic_position', 'gene_type']
    success = create_or_update_and_remove(new_bioentities, key_to_bioentity, values_to_check, new_session)
    return success
        
def convert_bioentevidence(new_session, old_bioentevidence):
    '''
    Convert Bioentevidence
    '''
    from model_new_schema.bioentity import Bioentevidence as NewBioentevidence, Bioentity as NewBioentity
    from model_new_schema.reference import Reference as NewReference

    #Cache bioentevidence
    key_to_bioentevidence = cache_by_key(NewBioentevidence, new_session)
    id_to_reference = cache_by_id(NewReference, new_session)
    id_to_bioent = cache_by_id(NewBioentity, new_session)
    
    #Create new bioentevidence if they don't exist, or update the database if they do.
    new_bioentevidence = [create_bioentevidence(x, id_to_reference, id_to_bioent) for x in old_bioentevidence]
    success = create_or_update_and_remove(new_bioentevidence, key_to_bioentevidence, ['reference_id', 'source', 'topic', 'bioent_id', 'date_created', 'created_by'], new_session)    
    return success

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker)   
   

