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
real_bioent_types = set(['ARS', 'CENTROMERE', 'GENE_CASSETTE', 'LONG_TERMINAL_REPEAT', 'MATING_LOCUS', 
                         'MULTIGENE_LOCUS', 'NCRNA', 'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED',
                         'ORF', 'PSEUDOGENE', 'RETROTRANSPOSON', 'RRNA', 'SNORNA', 'SNRNA', 'TELOMERE', 'TELOMERIC_REPEAT',
                         'TRANSPOSABLE_ELEMENT_GENE', 'TRNA', 'X_ELEMENT_COMBINATORIAL_REPEATS', 'X_ELEMENT_CORE_SEQUENCE',
                         "Y'_ELEMENT"])
def create_gene_type(old_feature_type):
    bioent_type = old_feature_type.upper()
    bioent_type = bioent_type.replace (" ", "_")
    if bioent_type in real_bioent_types:
        return bioent_type
    else:
        return None
    
def create_bioentity(old_bioentity):
    from model_new_schema.bioentity import Gene as NewGene
    
    display_name = old_bioentity.gene_name
    if display_name is None:
        display_name = old_bioentity.name
    
    qualifier = None
    attribute = None
    short_description = None
    headline = None
    description = None
    genetic_position = None
    
    ann = old_bioentity.annotation
    if ann is not None:
        qualifier = ann.qualifier
        attribute = ann.attribute
        short_description = ann.name_description
        headline = ann.headline
        description = ann.description
        genetic_position = ann.genetic_position
        
    gene_type = create_gene_type(old_bioentity.type)
    if gene_type is None:
        return None
    
    bioent = NewGene(old_bioentity.id, display_name, old_bioentity.name, old_bioentity.dbxref_id, old_bioentity.source, old_bioentity.status, 
                         gene_type, qualifier, attribute, short_description, headline, description, genetic_position, 
                         old_bioentity.date_created, old_bioentity.created_by)
    return bioent 

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
   

