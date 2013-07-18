'''
Created on Jul 3, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion import create_or_update_and_remove, \
    prepare_schema_connection, execute_conversion, \
    cache_references, cache_by_key_in_range, cache_link_by_id
from schema_conversion.output_manager import write_to_output_file
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
import model_new_schema
import model_old_schema

def create_bioentevidence_id(old_bioentevidence_id):
    return old_bioentevidence_id + 2000000

def create_bioentevidence(old_bioentevidence, reference_id_to_link, bioent_id_to_link):
    from model_new_schema.litguide import Bioentevidence as NewBioentevidence
    
    reference_id = old_bioentevidence.litguide.reference_id
    if reference_id not in reference_id_to_link:
        print 'Reference does not exist. ' + str(reference_id)
        return None
    reference_link, reference_citation = reference_id_to_link[reference_id]
    
    bioent_id = old_bioentevidence.feature_id
    if bioent_id not in bioent_id_to_link:
        print 'Bioentity does not exist. ' + str(bioent_id)
        return None
    bioent_link = bioent_id_to_link[bioent_id]
    
    new_id = create_bioentevidence_id(old_bioentevidence.id)
    topic = old_bioentevidence.litguide.topic
    
    new_bioentevidence = NewBioentevidence(new_id, reference_id, reference_link, reference_citation,
                                           topic, bioent_id, bioent_link,
                                           old_bioentevidence.date_created, old_bioentevidence.created_by)
    return new_bioentevidence

def convert(old_session_maker, new_session_maker, ask=True):
    from model_old_schema.reference import LitguideFeat as OldLitguideFeat
    
    intervals = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000]
    
    from model_new_schema.bioentity import Bioentity as NewBioentity
    new_session = new_session_maker()
    reference_id_to_link = cache_references(new_session)
    bioent_id_to_link = cache_link_by_id(NewBioentity, new_session)
    
    
    # Convert Litguide Evidence
    write_to_output_file( 'Litguide Evidence')
    for i in range(0, len(intervals)-1):
        min_id = intervals[i]
        max_id = intervals[i+1]
        execute_conversion(convert_bioentevidence, old_session_maker, new_session_maker, ask,
                min_id = lambda old_session: min_id,
                max_id = lambda old_session: max_id,
                reference_id_to_link = lambda old_session: reference_id_to_link,
                bioent_id_to_link = lambda old_session: bioent_id_to_link,
                old_bioentevidence= lambda old_session: old_session.query(OldLitguideFeat).filter(
                            or_(OldLitguideFeat.topic=='Additional Literature',
                                OldLitguideFeat.topic=='Primary Literature',
                                OldLitguideFeat.topic=='Omics',
                                OldLitguideFeat.topic=='Reviews')).options(joinedload('litguide')).filter(
                            OldLitguideFeat.feature_id >=min_id).filter(
                            OldLitguideFeat.feature_id < max_id).all())
        
def convert_bioentevidence(new_session, old_bioentevidence, reference_id_to_link, bioent_id_to_link, min_id, max_id):
    '''
    Convert Bioentevidence
    '''
    from model_new_schema.litguide import Bioentevidence as NewBioentevidence

    #Cache bioentevidence
    key_to_bioentevidence = cache_by_key_in_range(NewBioentevidence, NewBioentevidence.bioent_id, new_session, min_id, max_id)
    
    #Create new bioentevidence if they don't exist, or update the database if they do.
    new_bioentevidence = [create_bioentevidence(x, reference_id_to_link, bioent_id_to_link) for x in old_bioentevidence]
    
    values_to_check = ['experiment_id', 'experiment_name_with_link',
                       'reference_id', 'reference_name_with_link', 'reference_citation',
                       'evidence_type', 'strain_id', 'strain_name_with_link', 
                       'source', 'topic', 'bioent_id', 'bioent_name_with_link', 'date_created', 'created_by']
    success = create_or_update_and_remove(new_bioentevidence, key_to_bioentevidence, values_to_check, new_session)    
    return success

if __name__ == "__main__":
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(old_session_maker, new_session_maker, False)