from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import not_

from src.sgd.convert.config import log_directory


__author__ = 'kpaskov'

def prepare_schema_connection(model_cls, dbtype, dbhost, dbname, schema, dbuser, dbpass):
    class Base(object):
        __table_args__ = {'schema': schema, 'extend_existing':True}

    model_cls.Base = declarative_base(cls=Base)
    model_cls.Base.schema = schema
    model_cls.metadata = model_cls.Base.metadata
    engine_key = "%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname)
    engine = create_engine(engine_key, pool_recycle=3600)
    model_cls.Base.metadata.bind = engine
    session_maker = sessionmaker(bind=engine)

    return session_maker

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

def is_number(str_value):
    try:
        int(str_value)
        return True
    except:
        return False

def read_obo(filename):
    terms = []
    f = open(filename, 'r')
    current_term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if current_term is not None:
                terms.append(current_term)
            current_term = {}
        elif current_term is not None and ': ' in line:
            pieces = line.split(': ')
            if pieces[0] in current_term:
                current_term[pieces[0]] = [current_term[pieces[0]], pieces[1]]
            else:
                current_term[pieces[0]] = pieces[1]
    f.close()
    return terms

def clean_up_orphans(nex_session_maker, child_cls, parent_cls, class_type):
    nex_session = nex_session_maker()
    child_table_ids = nex_session.query(child_cls.id).subquery()
    query = nex_session.query(parent_cls).filter_by(class_type=class_type).filter(not_(parent_cls.id.in_(child_table_ids)))
    print 'Deleting orphans ' + class_type + ': ' + str(query.count())
    query.delete(synchronize_session=False)
    nex_session.commit()
    nex_session.close()
