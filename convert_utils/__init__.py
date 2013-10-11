'''
Created on Oct 10, 2013

@author: kpaskov
'''
from datetime import datetime
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
import logging
import model_new_schema
import model_old_schema
import sys

def check_session_maker(session_maker, DBHOST, is_old):
    if is_old:
        from model_old_schema.feature import Feature
        query = session_maker().query(Feature)
    else:
        from model_new_schema.bioentity import Bioentity
        query = session_maker().query(Bioentity)
    
    try:
        query.first()
    except:
        raise Exception("Connection to " + DBHOST + " failed. Please check your parameters.") 

def prepare_connections(need_old=True):
    from convert_all import config
    if need_old:
        OLD_DBHOST = sys.argv[1] + ':1521'
        OLD_DBUSER = sys.argv[2]
        OLD_DBPASS = sys.argv[3]
        NEW_DBHOST = sys.argv[4] + ':1521'
        NEW_DBUSER = sys.argv[5]
        NEW_DBPASS = sys.argv[6]
    
        old_session_maker = prepare_schema_connection(model_old_schema, config.OLD_DBTYPE, OLD_DBHOST, config.OLD_DBNAME, config.OLD_SCHEMA, 
                                                  OLD_DBUSER, OLD_DBPASS)
        check_session_maker(old_session_maker, OLD_DBHOST, True)
        
        new_session_maker = prepare_schema_connection(model_new_schema, config.NEW_DBTYPE, NEW_DBHOST, config.NEW_DBNAME, config.NEW_SCHEMA, 
                                                  NEW_DBUSER, NEW_DBPASS)
        check_session_maker(new_session_maker, NEW_DBHOST, False)
        return old_session_maker, new_session_maker
    else:
        NEW_DBHOST = sys.argv[1] + ':1521'
        NEW_DBUSER = sys.argv[2]
        NEW_DBPASS = sys.argv[3]
        
        new_session_maker = prepare_schema_connection(model_new_schema, config.NEW_DBTYPE, NEW_DBHOST, config.NEW_DBNAME, config.NEW_SCHEMA, 
                                                  NEW_DBUSER, NEW_DBPASS)
        check_session_maker(new_session_maker, NEW_DBHOST, False)
        return new_session_maker
    

def prepare_schema_connection(model_cls, DBTYPE, DBHOST, DBNAME, SCHEMA, DBUSER, DBPASS):
    model_cls.SCHEMA = SCHEMA
    class Base(object):
        __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    model_cls.Base = declarative_base(cls=Base)
    model_cls.metadata = model_cls.Base.metadata
    engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)
    model_cls.Base.metadata.bind = engine
    session_maker = sessionmaker(bind=engine)
        
    return session_maker
    
def check_value(new_obj, old_obj, field_name):
    new_obj_value = getattr(new_obj, field_name)
    old_obj_value = getattr(old_obj, field_name)

    if isinstance(new_obj_value, (int, long, float, complex)) and isinstance(old_obj_value, (int, long, float, complex)):
        if not float_approx_equal(new_obj_value, old_obj_value):
            setattr(old_obj, field_name, new_obj_value)
            return False
    elif new_obj_value != old_obj_value:
        setattr(old_obj, field_name, new_obj_value)
        return False
    return True

def check_values(new_obj, old_obj, field_names, output_creator, key):
    for field_name in field_names:
        if not check_value(new_obj, old_obj, field_name):
            output_creator.changed(key, field_name)
    
def add_or_check(new_obj, key_mapping, id_mapping, key, values_to_check, session, output_creator):
    if key in key_mapping:
        current_obj = key_mapping[key]
        check_values(new_obj, current_obj, values_to_check, output_creator, key)
        return False
    else:
        if new_obj.id in id_mapping:
            to_be_removed = id_mapping[new_obj.id]
            session.delete(to_be_removed)
        
        session.add(new_obj)
        key_mapping[key] = new_obj
        id_mapping[new_obj.id] = new_obj
        output_creator.added()
        return True
    
def create_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name
    
def float_approx_equal(x, y, tol=1e-18, rel=1e-7):
    #http://code.activestate.com/recipes/577124-approximately-equal/
    if tol is rel is None:
        raise TypeError('cannot specify both absolute and relative errors are None')
    tests = []
    if tol is not None: tests.append(tol)
    if rel is not None: tests.append(rel*abs(x))
    assert tests
    return abs(x - y) <= max(tests)

def break_up_file(filename, delimeter='\t'):
    rows = []
    f = open(filename, 'r')
    for line in f:
        rows.append(line.split(delimeter))
    f.close()
    return rows

def create_or_update(new_obj, current_obj_by_id, current_obj_by_key, values_to_check, session, output_creator):
    #If there's an object with the same key and it also has the same id, then that's our object - we just need to
    #check to make sure it's values match ours.
    if current_obj_by_key is not None and (new_obj.id is None or current_obj_by_key.id == new_obj.id):
        for value_to_check in values_to_check:
            if not check_value(new_obj, current_obj_by_key, value_to_check):
                output_creator.changed(current_obj_by_key.unique_key(), value_to_check)   
        return False 
    else:
        if current_obj_by_id is not None:
            session.delete(current_obj_by_id)
            print 'Removed ' + str(new_obj.id)
            output_creator.removed()
            session.commit()
        
        if current_obj_by_key is not None:
            session.delete(current_obj_by_key)
            print 'Removed' + str(new_obj.unique_key())
            output_creator.removed()
            session.commit()
            
        session.add(new_obj)
        output_creator.added()
        return True
        
def set_up_logging(label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.DEBUG, datefmt='%m/%d/%Y %H:%M:%S')
    
    log = logging.getLogger(label)
    
    hdlr = logging.FileHandler('/Users/kpaskov/Documents/Schema Conversion Logs/' + label + '.' + str(datetime.now()) + '.txt')
    formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s', '%m/%d/%Y %H:%M:%S')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr) 
    log.setLevel(logging.DEBUG)
    return log
