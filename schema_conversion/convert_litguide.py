'''
Created on Jul 3, 2013

@author: kpaskov
'''
from schema_conversion import ask_to_commit, cache_by_key, cache_by_id, \
    create_or_update_and_remove
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
import datetime

def create_bioentevidence_id(old_bioentevidence_id):
    return old_bioentevidence_id + 1530000

def create_bioentevidence(old_bioentevidence, id_to_reference, id_to_bioentity):
    from model_new_schema.bioentity import Bioentevidence as NewBioentevidence
    
    reference_id = old_bioentevidence.litguide.reference_id
    if reference_id not in id_to_reference:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    
    bioent_id = old_bioentevidence.feature_id
    if bioent_id not in id_to_bioentity:
        print 'Bioentity does not exist. ' + str(bioent_id)
        return None
    
    new_id = create_bioentevidence_id(old_bioentevidence.id)
    topic = old_bioentevidence.litguide.topic
    
    new_bioentevidence = NewBioentevidence(new_id, reference_id, topic, bioent_id, 
                                           old_bioentevidence.date_created, old_bioentevidence.created_by)
    return new_bioentevidence

def convert(old_session_maker, new_session_maker):
    from model_old_schema.reference import LitguideFeat as OldLitguideFeat
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