'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the KPASKOV schema on fasolt.
'''
from connection_test.config import DBTYPE, DBHOST, DBNAME
from model_new_schema import metadata
from model_new_schema.config import DBUSER, DBPASS
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from time import time
# imports of model classes from model.feature, model.taxonomy, etc are done as needed, since these imports are
# not available until AFTER the metadata is bound to the engine.

class DBConnection(object):
    '''
    This class acts as a divider between the Oracle back-end and the application. In order to pull information
    from the Oracle DB, this class MUST be called.
    '''
    engine = None
    SessionFactory = None

         
    def __init__(self, username, password):
        #Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True)
        metadata.bind = self.engine
        self.SessionFactory = sessionmaker(bind=self.engine)
        return
    
    def isConnected(self):
        #Checks if a connection to the db has been made.
        return self.engine is not None
    
    def getFirstBioentity(self):
        #Get the first Feature.
        from model_new_schema.bioentity_declarative import Bioentity
        session = self.SessionFactory()
        return session.query(Bioentity).first()
    
    def getBioentityByName(self, name):
        #Get the first Feature.
        from model_new_schema.bioentity_declarative import Bioentity
        session = self.SessionFactory()
        return session.query(Bioentity).filter_by(name=name).all();
    
    def getBioentityCount(self):
        #Get the first Feature.
        from model_new_schema.bioentity_declarative import Bioentity
        session = self.SessionFactory()
        return session.query(Bioentity).count()
    def getBioentities(self):
        #Get the first Feature.
        from model_new_schema.bioentity_declarative import Bioentity
        session = self.SessionFactory()
        return session.query(Bioentity).all()

    
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
    conn = DBConnection(DBUSER, DBPASS)
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

if __name__ == '__main__':
    conn = DBConnection(DBUSER, DBPASS)
    b = conn.getBioentityByName('GRD16')[0]
    print b
    print b.name
    

    
    