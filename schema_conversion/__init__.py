from numbers import Number
from schema_conversion.output_manager import OutputCreator
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.types import Float
from utils.utils import float_approx_equal
import datetime

def prepare_schema_connection(model_cls, config_cls):
    model_cls.SCHEMA = config_cls.SCHEMA
    class Base(object):
        __table_args__ = {'schema': config_cls.SCHEMA, 'extend_existing':True}

    model_cls.Base = declarative_base(cls=Base)
    model_cls.metadata = model_cls.Base.metadata
    engine = create_engine("%s://%s:%s@%s/%s" % (config_cls.DBTYPE, config_cls.DBUSER, config_cls.DBPASS, config_cls.DBHOST, config_cls.DBNAME), convert_unicode=True, pool_recycle=3600)
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

def cache(cls, session, **kwargs):
    cache_entries = dict([(x.unique_key(), x) for x in session.query(cls).filter_by(**kwargs).all()])
    return cache_entries
    
def add_or_check(new_obj, mapping, key, values_to_check, session, output_creator):
    if key in mapping:
        current_obj = mapping[key]
        check_values(new_obj, current_obj, values_to_check, output_creator, key)
        return False
    else:
        session.add(new_obj)
        mapping[key] = new_obj
        output_creator.added()
        return True
    
def create_or_update(new_objs, mapping, values_to_check, session):
    output_creator = OutputCreator()
    
    for new_obj in new_objs:
        key = new_obj.unique_key()
        add_or_check(new_obj, mapping, key, values_to_check, session, output_creator)
    output_creator.finished()
    
def create_or_update_and_remove(new_objs, mapping, values_to_check, session):
    output_creator = OutputCreator()
    to_be_removed = set(mapping.keys())

    
    # Check old objects or add new objects.
    for new_obj in new_objs:
        key = new_obj.unique_key()
        add_or_check(new_obj, mapping, key, values_to_check, session, output_creator)
            
        if key in to_be_removed:
            to_be_removed.remove(key)
            
    for r_id in to_be_removed:
        session.delete(mapping[r_id])
        output_creator.removed()
    output_creator.finished()
    
def ask_to_commit(new_session, start_time):
    pause_begin = datetime.datetime.now()
    user_input = None
    while user_input != 'Y' and user_input != 'N':
        user_input = raw_input('Commit these changes (Y/N)?')
    pause_end = datetime.datetime.now()
    if user_input == 'Y':
        new_session.commit()
    end_time = datetime.datetime.now()
    print str(end_time - pause_end + pause_begin - start_time) + '\n'
    
    
    