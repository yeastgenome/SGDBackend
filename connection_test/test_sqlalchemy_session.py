'''
Created on Oct 18, 2012

@author: kpaskov
'''
from connection_test.config import DBTYPE, DBHOST, DBNAME, SCHEMA
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import MetaData, Table


Base = declarative_base()
metadata = MetaData()  
engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, "OTTO", "db4auto", DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)
metadata.bind = engine
  
class Feature(Base):
    __table__ = Table('feature', metadata, autoload = True, schema = SCHEMA)

    #Values
    id = __table__.c.feature_no
    name = __table__.c.feature_name
    type = __table__.c.feature_type
    source = __table__.c.source
    status = __table__.c.status
    gene_name = __table__.c.gene_name
      
class Test(object):
    SessionFactory = None
   
    def __init__(self):
        #Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        self.SessionFactory = sessionmaker(bind=engine)
        return
    

    
    def getFirstFeature(self):
        #Get the first Feature.
        session = self.SessionFactory()
        return session.query(Feature).first()

   
    
    
        
if __name__ == '__main__':
    conn = Test()
    print conn.getFirstFeature().name
    
    