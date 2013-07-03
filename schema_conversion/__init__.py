from numbers import Number
from schema_conversion.output_manager import OutputCreator
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.types import Float
import datetime
import sys

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

def cache_by_key(cls, session, **kwargs):
    cache_entries = dict([(x.unique_key(), x) for x in session.query(cls).filter_by(**kwargs).all()])
    return cache_entries

def cache_by_key_in_range(cls, col, session, min_id, max_id):
    cache_entries = dict([(x.unique_key(), x) for x in session.query(cls).filter(col >= min_id).filter(col < max_id).all()])
    return cache_entries

def cache_by_id(cls, session, **kwargs):
    cache_entries = dict([(x.id, x) for x in session.query(cls).filter_by(**kwargs).all()])
    return cache_entries

def cache_ids(cls, session, **kwargs):
    cache_ids = session.query(cls.id).filter_by(**kwargs).all()
    return cache_ids
    
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
    new_objs = filter(None, new_objs)
    output_creator = OutputCreator()
    
    to_be_added = set([new_obj.id for new_obj in new_objs if new_obj.unique_key() not in mapping])
    problem_objs = [old_obj for old_obj in mapping.values() if old_obj.id in to_be_added]
    if len(problem_objs) > 0:
        print str(len(problem_objs)) + ' problem objects exist and must be deleted to continue.'
        print [problem.id for problem in problem_objs]
        for obj in problem_objs:
            session.delete(obj)
        return False
    else:
        # Check old objects or add new objects.
        for new_obj in new_objs:
            key = new_obj.unique_key()
            add_or_check(new_obj, mapping, key, values_to_check, session, output_creator)
            
        output_creator.finished()
        return True
    
def create_or_update_and_remove(new_objs, mapping, values_to_check, session, full_mapping=None):
    if full_mapping is None:
        full_mapping = mapping
    
    new_objs = filter(None, new_objs)
    new_objs.sort()
    output_creator = OutputCreator()
    to_be_removed = set(mapping.keys())
    
    to_be_added = set([new_obj.id for new_obj in new_objs if new_obj.unique_key() not in mapping])
    problem_objs = [old_obj for old_obj in mapping.values() if old_obj.id in to_be_added]
    if len(problem_objs) > 0:
        print str(len(problem_objs)) + ' problem objects exist and must be deleted to continue.'
        print [problem.id for problem in problem_objs]
        for obj in problem_objs:
            session.delete(obj)
        return False
    else:
        # Check old objects or add new objects.
        for new_obj in new_objs:
            key = new_obj.unique_key()
            add_or_check(new_obj, full_mapping, key, values_to_check, session, output_creator)
            
            if key in to_be_removed:
                to_be_removed.remove(key)
            
        for r_id in to_be_removed:
            session.delete(mapping[r_id])
            output_creator.removed()
        output_creator.finished()
        return True
    
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
    
def commit_without_asking(new_session, start_time):
    new_session.commit()
    end_time = datetime.datetime.now()
    print str(end_time - start_time) + '\n'
    
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

def execute_conversion(convert_f, old_session_maker, new_session_maker, ask, **kwargs):
    start_time = datetime.datetime.now()
    try:
        old_session = old_session_maker()
        kwargs = dict([(x, y(old_session)) for x, y in kwargs.iteritems()])
        success = False
        while not success:
            new_session = new_session_maker()
            success = convert_f(new_session, **kwargs)
            if ask:
                ask_to_commit(new_session, start_time)  
            else:
                commit_without_asking(new_session, start_time)
            new_session.close()
    except Exception:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        old_session.close()
        new_session.close()    