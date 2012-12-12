'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the KPASKOV schema on fasolt.
'''
#from connection_test.config import DBTYPE, DBHOST, DBNAME
from model_new_schema import metadata, engine
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity_declarative import Bioentity
from model_new_schema.biorelation import Biorelation
from model_new_schema.jsonify import jsonify_obj
from sqlalchemy.orm.session import sessionmaker
import sys
import traceback

class Model(object):
    '''
    This class acts as a divider between the Oracle back-end and the application. In order to pull information
    from the Oracle DB, this class MUST be called.
    '''
    engine = None
    SessionFactory = None
     
    def __init__(self):
        #Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        #self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True)
        #self.engine = create_engine('mysql://root@localhost/sgd_db')
        self.engine = engine
        metadata.bind = self.engine
        self.SessionFactory = sessionmaker(bind=self.engine)
        return
    
    def isConnected(self):
        #Checks if a connection to the db has been made.
        return self.engine is not None
    
    def execute(self, f):
        try:
            session = self.SessionFactory()
            return f(session)
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            session.close()
    
def prepare(f, session):
    if session is None:
        return f
    else:
        return f(session)

def get(model, session=None, **kwargs):
    def f(session):
        return session.query(model).filter_by(**kwargs).all()
    
    return prepare(f, session)
    
def get_first(model, session=None, **kwargs):
    def f(session):
        return session.query(model).filter_by(**kwargs).first()
    
    return prepare(f, session)

def create(model, session=None, **kwargs):
    def f(session):
        return model(session=session, **kwargs)
    
    return prepare(f, session)

def count(model, session=None, **kwargs):
    def f(session):
        return session.query(model).filter_by(**kwargs).count()
    
    return prepare(f, session)
    
def get_or_create(model, session=None, **kwargs):
    def f(session):
        instance = get_first(session, model, **kwargs)
        if instance:
            return instance
        else:
            instance = create(session, model, **kwargs)
            return instance
    return f
   
    return prepare(f, session)

def test(session=None):
    def f(session):
        return get_first(Bioentity, session=session)

    return prepare(f, session)

def jsonify(g, full=True, session=None):
    def f(session):
        return jsonify_obj(g(session=session), full)
    
    return prepare(f, session)

if __name__ == '__main__':
    conn = Model()
    print conn.execute(test())
    print conn.execute(jsonify(test()))
    #first_orf_for_first_go_term_for_bioentity_with_name = lambda session: conn.getByName(session, Bioentity, 'AAH1')[0].go_terms[0].orfs[0]
    #json1 = conn.execute(first_orf_for_first_go_term_for_bioentity_with_name)
    #first_orf_for_first_go_term_for_bioentity_with_name2 = lambda session: conn.getByField(session, Bioentity, 'name', 'AAH1')[0].go_terms[0].orfs[0]
    #json2 = conn.execute(first_orf_for_first_go_term_for_bioentity_with_name2)
    #print json1.__class__.__name__
    #print json1
    #print json.loads(json1).keys()
    #first_orf_for_first_go_term_for_bioentity_with_name = lambda session: get(Bioentity, name='AAH1')[0].go_terms[0].orfs[0]
    #json1 = conn.execute(first_orf_for_first_go_term_for_bioentity_with_name)
    #print json1
    #print "TEST"
    #testingFunction = lambda session: test(session)
    #testResult = conn.execute(test())

    #print testResult
    #print json2.__class__.__name__
    #print json2
    #orf1 = json_to_object(json1)
    #orf2 = json_to_object(json2)
    #print orf1
    #print orf1 == orf2
    

    
    