'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the KPASKOV schema on fasolt.
'''
#from connection_test.config import DBTYPE, DBHOST, DBNAME
from model_new_schema import Base
from model_new_schema.config import DBTYPE, DBHOST, DBNAME, SCHEMA, DBUSER, \
    DBPASS
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import model_new_schema

class DBConnectionLostException(Exception):
    def __init__(self):
        self.message = "The connection to the database has been lost. Please try logging in again."
    def __str__(self):
        return repr(self.message)
    
class Model(object):
    '''
    This class acts as a divider between the Oracle back-end and the application. In order to pull information
    from the Oracle DB, this class MUST be called.
    '''
    user_to_sessionmaker = {}

    def __init__(self, dbtype, dbhost, dbname, dbschema):
        self.dbtype = dbtype
        self.dbhost = dbhost
        self.dbname = dbname
        model_new_schema.SCHEMA = dbschema
        
        class Base(object):
            __table_args__ = {'schema': dbschema, 'extend_existing':True}

        model_new_schema.Base = declarative_base(cls=Base)
        model_new_schema.metadata = model_new_schema.Base.metadata
    
    def connect(self, username, password):
        """
        Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        """
        engine = create_engine("%s://%s:%s@%s/%s" % (self.dbtype, username, password, self.dbhost, self.dbname), convert_unicode=True, pool_recycle=3600)
        
        
        model_new_schema.Base.metadata.bind = engine
        self.user_to_sessionmaker[username] = sessionmaker(bind=engine)
        
        return
    
    def is_connected(self, username):
        #Checks if a connection to the db has been made.
        try:
            sessionmaker = self.user_to_sessionmaker[username] 
            if sessionmaker is None:
                return False
            self.user_to_sessionmaker[username]().get_bind().connect()
            return True
        except:      
            return False
        
    def execute(self, f, username, commit=False, **kwargs):
        if not self.is_connected(username):
            raise DBConnectionLostException()
        try:
            session = self.user_to_sessionmaker[username]()
            session.user = username.upper()
            response = f(session, **kwargs)
            if commit:
                session.commit()
            return response
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
def get(model, session=None, **kwargs):
    def f(session):
        return session.query(model).filter_by(**kwargs).all()
    
    return f if session is None else f(session)
    
def get_first(model, session=None, **kwargs):
    def f(session):
        return session.query(model).filter_by(**kwargs).first()
    
    return f if session is None else f(session)

def count(model, session=None, **kwargs):
    def f(session):
        return session.query(model).filter_by(**kwargs).count()
    
    return f if session is None else f(session)

def exists(model, session=None, **kwargs):
    def f(session):
        return count(model, session, **kwargs) > 0
    
    return f if session is None else f(session)

def add(obj, session=None):
    def f(session):
        session.add(obj)
        return
    
    return f if session is None else f(session)

def delete(obj, session=None, **kwargs):
    def f(session):
        session.delete(obj)
        return
    
    return f if session is None else f(session)

def jsonify(g, full=True, session=None):
    def f(session):
        from model_new_schema.jsonify import jsonify_obj
        return jsonify_obj(g(session=session), full)
    
    return f if session is None else f(session)

if __name__ == "__main__":
    model = Model(DBTYPE, DBHOST, DBNAME, SCHEMA)
    model.connect(DBUSER, DBPASS)
    
    def g(session=None):
        from bioentity import Bioentity
        def f(session):
            bioent = get_first(Bioentity, session=session)
            return bioent.bioconcepts
        return f if session is None else f(session)
    
    print model.execute(g(), 'sprout')
