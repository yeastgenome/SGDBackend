'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the KPASKOV schema on fasolt.
'''
#from connection_test.config import DBTYPE, DBHOST, DBNAME
from model_new_schema import metadata
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity_declarative import Bioentity
from model_new_schema.biorelation import Biorelation
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from time import time
import json
#from model_new_schema.config import DBUSER, DBPASS



# imports of model classes from model.feature, model.taxonomy, etc are done as needed, since these imports are
# not available until AFTER the metadata is bound to the engine.

class DBConnection(object):
    '''
    This class acts as a divider between the Oracle back-end and the application. In order to pull information
    from the Oracle DB, this class MUST be called.
    '''
    engine = None
    SessionFactory = None

         
    def __init__(self):
        #Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        #self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True)
        self.engine = create_engine('mysql://root@localhost/sgd_db')
        metadata.bind = self.engine
        self.SessionFactory = sessionmaker(bind=self.engine)
        return
    
    def isConnected(self):
        #Checks if a connection to the db has been made.
        return self.engine is not None
    
    def getByName(self, session, cls, name):
        return session.query(cls).filter_by(name=name).all();
    
    def getByID(self, session, cls, iD):
        return session.query(cls).filter_by(id=iD).all();
    
    def getAll(self, session, cls):
        return session.query(cls).all();
    
    def getCount(self, session, cls):
        session = self.SessionFactory()
        return session.query(cls).count()
    
    def execute(self, f):
        session = self.SessionFactory()
        x = json.dumps(f(session))
        session.close()
        return x
    

    
def timeInheritance(bioentity):
    begin = time()
    a = time()-begin
    #print 'Time to grab Bioentity\n'
    
    begin = time()
    bioentity.name
    b = time()-begin
    #print 'Time to grab name\n'
    
    c = None
    if hasattr(bioentity, 'description'):
        begin = time()
        bioentity.description
        c = time()-begin
        #print 'Time to grab description\n'
    
    d = None
    if hasattr(bioentity, 'crick_data'): 
        begin = time()
        bioentity.crick_data
        d = time()-begin
        #print 'Time to grab crick data\n'
    
    return [a, b, c, d]
        
def timeInheritanceAcrossAllBioentites():
    conn = DBConnection()
    sumTotal = [0, 0, 0, 0]
    count = [0, 0, 0, 0]
    for bioentity in conn.getBioentities():
        times = timeInheritance(bioentity)
        for index, value in enumerate(times):
            if value is not None:
                sumTotal[index] = sumTotal[index] + value
                count[index] += 1

    print sum[0]/count[0]
    print 'Time to grab Bioentity\n'
    print sum[1]/count[1]
    print 'Time to grab name\n'
    print sum[2]/count[2]
    print 'Time to grab description\n'
    print sum[3]/count[3]
    print 'Time to grab crick data\n'
    
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
    return instance

if __name__ == '__main__':
    conn = DBConnection()
    b = lambda session: conn.getByName(session, Bioentity, 'ACT1')[0].go_terms[0].orfs[0]
    orf = conn.execute(b)
    print orf
    

    
    