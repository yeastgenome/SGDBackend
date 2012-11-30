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
import json
import jsonpickle
#from model_new_schema.config import DBUSER, DBPASS



# imports of model classes from model.feature, model.taxonomy, etc are done as needed, since these imports are
# not available until AFTER the metadata is bound to the engine.

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
        obj = f(session)
        json_obj = object_to_json(obj, recoverable=False)
        session.close()
        return json_obj
    
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
    return instance

def json_to_object(json):
    return jsonpickle.decode(json)

def object_to_json(obj, recoverable=False):
    if not recoverable:
        pickled = jsonpickle.encode(obj.serialize(), unpicklable=False, max_depth=3)
        json_dict = json.loads(pickled)
        if '_sa_instance_state' in json_dict:
            del json_dict['_sa_instance_state']
        return json.dumps(json_dict)
    else:
        pickled = jsonpickle.encode(obj, unpicklable=True)
        return pickled
    

if __name__ == '__main__':
    conn = Model()
    first_orf_for_first_go_term_for_bioentity_with_name = lambda session: conn.getByName(session, Bioentity, 'AAH1')[0].go_terms[0].orfs[0]
    json1 = conn.execute(first_orf_for_first_go_term_for_bioentity_with_name)
    first_orf_for_first_go_term_for_bioentity_with_name2 = lambda session: conn.getByName(session, Bioentity, 'AAH1')[0].go_terms[0].orfs[0]
    json2 = conn.execute(first_orf_for_first_go_term_for_bioentity_with_name2)
    print json1.__class__.__name__
    print json1
    print json.loads(json1).keys()

    print json2.__class__.__name__
    print json2
    orf1 = json_to_object(json1)
    orf2 = json_to_object(json2)
    print orf1
    print orf1 == orf2
    

    
    