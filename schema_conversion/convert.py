'''
Created on Jan 16, 2013

@author: kpaskov
'''
from model_new_schema import config as new_config
from model_old_schema import config as old_config
from schema_conversion.convert_phenotype import convert_phenotype
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import model_new_schema
import model_old_schema




def convert():    
    commit=True
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    old_session_maker = prepare_schema_connection(model_old_schema, old_config)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()
        
        #convert_feature(old_session, new_session)
        #convert_transcript(old_session, new_session)
        #convert_protein(old_session, new_session)
        #convert_dna_sequence(old_session, new_session)
        convert_phenotype(old_session, new_session)
        #convert_reference(old_session, new_session)
        #add_bioents_to_typeahead(new_session)
                
        if commit:
            new_session.commit()
    finally:
        new_session.close()

def prepare_schema_connection(model_cls, config_cls):
    model_cls.SCHEMA = config_cls.SCHEMA
    class Base(object):
        __table_args__ = {'schema': config_cls.SCHEMA, 'extend_existing':True}

    model_cls.Base = declarative_base(cls=Base)
    model_cls.metadata = model_cls.Base.metadata
    engine = create_engine("%s://%s:%s@%s/%s" % (config_cls.DBTYPE, config_cls.DBUSER, config_cls.DBPASS, config_cls.DBHOST, config_cls.DBNAME), convert_unicode=True, pool_recycle=3600)
    model_cls.Base.metadata.bind = engine
    session_maker = sessionmaker(bind=engine)
        
    return session_maker
  

    
if __name__ == "__main__":
    convert()