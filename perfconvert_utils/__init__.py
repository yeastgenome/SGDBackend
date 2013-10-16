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

def prepare_connections():
    from perfconvert import config
    
    DBHOST = sys.argv[1] + ':1521'
    DBUSER = sys.argv[2]
    DBPASS = getpass.getpass('DB User Password:')
        
    engine = create_engine("%s://%s:%s@%s/%s" % (config.DBTYPE, DBUSER, DBPASS, DBHOST, config.DBNAME), convert_unicode=True, pool_recycle=3600)
    meta = MetaData()
    meta.reflect(bind=engine)
        
    check_engine(engine, meta, DBHOST)
    return engine, meta
