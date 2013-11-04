from convert_utils.output_manager import OutputCreator
from datetime import datetime
from numbers import Number
from perfconvert_utils import config_passwords
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Float
import getpass
import json
import logging
import model_perf_schema
import requests
import sys

def set_up_logging(label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %H:%M:%S')
    
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)
    
    log = logging.getLogger(label)
    
    hdlr = logging.FileHandler('convert_logs/' + label + '.' + str(datetime.now()) + '.txt')
    formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s', '%m/%d/%Y %H:%M:%S')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr) 
    log.setLevel(logging.INFO)
    return log

def check_session_maker(session_maker, DBHOST):
    from model_perf_schema.core import Bioentity
    query = session_maker().query(Bioentity)
    query.first()
    try:
        query.first()
    except:
        raise Exception("Connection to " + DBHOST + " failed. Please check your parameters.") 

def prepare_connections(NEW_DBHOST):     
    new_session_maker = prepare_schema_connection(model_perf_schema, config_passwords.NEW_DBTYPE, NEW_DBHOST, config_passwords.NEW_DBNAME, config_passwords.NEW_SCHEMA, 
                                              config_passwords.NEW_DBUSER, config_passwords.NEW_DBPASS)
    check_session_maker(new_session_maker, NEW_DBHOST)
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
