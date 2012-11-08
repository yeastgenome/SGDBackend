'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the BUD schema on fasolt.

'''
from connection_test.config import DBTYPE, DBHOST, DBNAME
from model_old_schema import Base
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
# imports of model classes from model.feature, model.taxonomy, etc are done as needed, since these imports are
# not available until AFTER the metadata is bound to the engine.

class DBConnection(object):
    '''
    This class acts as a divider between the Oracle back-end and the application. In order to pull information
    from the Oracle DB, this class MUST be called.
    '''
    engine = None
    SessionFactory = None

         
    def connect(self, username, password):
        #Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True)
        Base.metadata.bind = self.engine
        self.SessionFactory = sessionmaker(bind=self.engine)
        return
    
    def isConnected(self):
        #Checks if a connection to the db has been made.
        try:
            self.engine.connect()
            return True
        except:
            return False
    
    def getFeatureByName(self, name):
        #Get a feature by its name.
        from model_old_schema.feature import Feature
        session = self.SessionFactory()
        return session.query(Feature).filter_by(name=name).first();
    
    def getRefTempByPmid(self, pubmed_id):
        #Get a feature by its name.
        from model_old_schema.reference import RefTemp
        session = self.SessionFactory()
        return session.query(RefTemp).filter_by(pubmed_id=pubmed_id).first();
    
    def getRefTemps(self):
        #Get all RefTemps.
        from model_old_schema.reference import RefTemp
        session = self.SessionFactory()
        return session.query(RefTemp).all()
    
    def moveRefTempToRefBad(self, pubmed_id):
        #Get the first RefBad.
        session = self.SessionFactory()
        try:       
            r_temp = self.getRefTempByPmid(pubmed_id)
            session.add(r_temp.createRefBad())
            session.delete(r_temp)
            session.commit()
            return True
        except:
            session.rollback()
            return False
    
    