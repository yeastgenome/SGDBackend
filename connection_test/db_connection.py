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

class DBConnection(object):
    '''
    classdocs
    '''
    engine = None
    metadata = None
    refTemps = None
    refBads = None
    abstracts = None
    users = None
    references = None

         
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
    
    def isConnect(self):
        #Checks if a connection to the db has been made.
        return self.engine is not None
    
    def getFirstAbstract(self):
        absts = self.abstracts.select().execute()
        return absts.first()
        
    def getRefTemps(self):
        #Get all refTemps from db.
        refs = list()
        for row in self.refTemps.select().execute():
            refs.append(row)
        return refs;
    
    def discardRef(self, pmid):
        refDiscarded = False
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            conn.execute(self.refTemps.delete().where(self.refTemps.c.pubmed==pmid))
            conn.execute(self.refBads.insert(), pubmed=pmid, created_by=current_user.name.upper(), date_created=datetime.datetime.now())
            trans.commit()
            refDiscarded = True
        except:
            trans.rollback()
            raise
        finally:
            trans.close()
            conn.close()
        return refDiscarded

    
    
    
        
if __name__ == '__main__':
    connection = DBConnection(DBUSER, DBPASS)
    connection.getFirstAbstract();
    time.sleep(10)
    connection.getFirstAbstract();
    time.sleep(9000)
    connection.getFirstAbstract();
    