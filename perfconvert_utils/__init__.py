from convert_utils import link_maker
from convert_utils.output_manager import OutputCreator
from datetime import datetime
from numbers import Number
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Float
import getpass
import json
import logging
import requests
import sys

def get_json(url, data=None):
    if data is not None:
        headers = {'Content-type': 'application/json; charset=utf-8"', 'processData': False}
        r = requests.post(url, data=json.dumps(data), headers=headers)
    else:
        r = requests.get(url)
    return r.json()

def get_json_str(url, data=None):
    if data is not None:
        headers = {'Content-type': 'application/json; charset=utf-8"', 'processData': False}
        r = requests.post(url, data=json.dumps(data), headers=headers)
    else:
        r = requests.get(url)
    return r.text

def set_up_logging(label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %H:%M:%S')
    
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
    
    log = logging.getLogger(label)
    
    hdlr = logging.FileHandler('/Users/kpaskov/Documents/Schema Conversion Logs/' + label + '.' + str(datetime.now()) + '.txt')
    formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s', '%m/%d/%Y %H:%M:%S')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr) 
    log.setLevel(logging.INFO)
    return log

def check_engine(engine, meta, DBHOST):
    table = meta.tables['bioentity']
    query = select([table.c.json])
    
    try:
        engine.execute(query).fetchone()
    except:
        raise Exception("Connection to " + DBHOST + " failed. Please check your parameters.") 
    
def check_backend_url(backend_url):
    if backend_url is None:
        raise Exception("Connection to " + backend_url + " failed. Please check your parameters.")

def prepare_connections():
    from perfconvert import config
    
    DBHOST = sys.argv[1] + ':1521'
    DBUSER = sys.argv[2]
    DBPASS = getpass.getpass('DB User Password:')
        
    engine = create_engine("%s://%s:%s@%s/%s" % (config.DBTYPE, DBUSER, DBPASS, DBHOST, config.DBNAME), convert_unicode=True, pool_recycle=3600)
    meta = MetaData()
    meta.reflect(bind=engine)
        
    check_engine(engine, meta, DBHOST)
    check_backend_url(sys.argv[3])
    link_maker.backend_start = sys.argv[3]
    return engine, meta
    
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

