'''
Created on Oct 18, 2012

@author: kpaskov
'''
from connection_test.config import DBTYPE, DBHOST, DBNAME, SCHEMA, DBUSER, \
    DBPASS
from flask_login import current_user
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData, Table
import datetime
import time

class Test(object):
    '''
    classdocs
    '''
    engine = None
    metadata = None
    abstracts = None

         
    def __init__(self, username, password):
        #Starts engine and sets up SQLAlchemy's ORM for all necessary tables.
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)
        self.metadata = MetaData(bind=self.engine)
        print self.metadata
        try:
            self.abstracts = Table('abstract', self.metadata, autoload = True, schema = SCHEMA)
            self.refTemps = Table('ref_temp', self.metadata, autoload = True, schema = SCHEMA)
            self.refBads = Table('ref_bad', self.metadata, autoload = True, schema = SCHEMA)
            self.users = Table('dbuser', self.metadata, autoload = True, schema = SCHEMA)
            self.references = Table('reference', self.metadata, autoload = True, schema = SCHEMA)
        except:
            raise
            
        return
    
    def getFirstAbstract(self):
        absts = self.abstracts.select().execute()
        return absts.first()

    
        
if __name__ == '__main__':
    connection = Test(DBUSER, DBPASS)
    print connection.getFirstAbstract();
    