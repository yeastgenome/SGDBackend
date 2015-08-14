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
    deleted_count = query.count()
    query.delete(synchronize_session=False)
    nex_session.commit()
    nex_session.close()
    return deleted_count

word_to_bioent_id = None

number_to_roman = {'01': 'I', '1': 'I',
                   '02': 'II', '2': 'II',
                   '03': 'III', '3': 'III',
                   '04': 'IV', '4': 'IV',
                   '05': 'V', '5': 'V',
                   '06': 'VI', '6': 'VI',
                   '07': 'VII', '7': 'VII',
                   '08': 'VIII', '8': 'VIII',
                   '09': 'IX', '9': 'IX',
                   '10': 'X',
                   '11': 'XI',
                   '12': 'XII',
                   '13': 'XIII',
                   '14': 'XIV',
                   '15': 'XV',
                   '16': 'XVI',
                   '17': 'Mito',
                   }

def get_word_to_bioent_id(word, nex_session):
    from src.sgd.model.nex.bioentity import Locus

    global word_to_bioent_id
    if word_to_bioent_id is None:
        word_to_bioent_id = {}
        for locus in nex_session.query(Locus).all():
            word_to_bioent_id[locus.format_name.lower()] = locus.id
            word_to_bioent_id[locus.display_name.lower()] = locus.id
            word_to_bioent_id[locus.format_name.lower() + 'p'] = locus.id
            word_to_bioent_id[locus.display_name.lower() + 'p'] = locus.id

    word = word.lower()
    return None if word not in word_to_bioent_id else word_to_bioent_id[word]

def get_bioent_by_name(bioent_name, to_ignore, nex_session):
    from src.sgd.model.nex.bioentity import Bioentity
    if bioent_name not in to_ignore:
        try:
            int(bioent_name)
        except ValueError:
            bioent_id = get_word_to_bioent_id(bioent_name, nex_session)
            return None if bioent_id is None else nex_session.query(Bioentity).filter_by(id=bioent_id).first()
    return None

def link_gene_names(text, to_ignore, nex_session):
    words = text.split(' ')
    new_chunks = []
    chunk_start = 0
    i = 0
    for word in words:
        bioent_name = word
        if bioent_name.endswith('.') or bioent_name.endswith(',') or bioent_name.endswith('?') or bioent_name.endswith('-'):
            bioent_name = bioent_name[:-1]
        if bioent_name.endswith(')'):
            bioent_name = bioent_name[:-1]
        if bioent_name.startswith('('):
            bioent_name = bioent_name[1:]

        bioent = get_bioent_by_name(bioent_name.upper(), to_ignore, nex_session)

        if bioent is not None:
            new_chunks.append(text[chunk_start: i])
            chunk_start = i + len(word) + 1

            new_chunk = "<a href='" + bioent.link + "'>" + bioent_name + "</a>"
            if word[-2] == ')':
                new_chunk = new_chunk + word[-2]
            if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-') or word.endswith(')'):
                new_chunk = new_chunk + word[-1]
            if word.startswith('('):
                new_chunk = word[0] + new_chunk
            new_chunks.append(new_chunk)
        i = i + len(word) + 1
    new_chunks.append(text[chunk_start: i])
    try:
        return ' '.join(new_chunks)
    except:
        print text
        return text


sgdid_to_reference_id = None

def get_sgdid_to_reference_id(sgdid, nex_session=None):
    from src.sgd.model.nex.reference import Reference
    global sgdid_to_reference_id
    if sgdid_to_reference_id is None:
        if nex_session is None:
            from src.sgd.model import nex
            from src.sgd.convert import config
            nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
            nex_session = nex_session_maker()
        sgdid_to_reference_id = {}
        for ref in nex_session.query(Reference).all():
            sgdid_to_reference_id[ref.sgdid] = ref.id
    return None if sgdid not in sgdid_to_reference_id else sgdid_to_reference_id[sgdid]

relation_to_ro_id = None

def get_relation_to_ro_id(relation_type, nex_session=None):
    from src.sgd.model.nex.ro import Ro
    global relation_to_ro_id
    if relation_to_ro_id is None:
        if nex_session is None:
            from src.sgd.model import nex
            from src.sgd.convert import config
            nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
            nex_session = nex_session_maker()
        relation_to_ro_id = {}
        for relation in nex_session.query(Ro).all():
            relation_to_ro_id[relation.display_name] = relation.id
    return None if relation_type not in relation_to_ro_id else relation_to_ro_id[relation_type]

word_to_strain_id = None

def get_word_to_strain_id(word, nex_session):
    from src.sgd.model.nex.misc import Strain

    global word_to_strain_id
    if word_to_strain_id is None:
        word_to_strain_id = {}
        for strain in nex_session.query(Strain).all():
            if strain.link is not None:
                word_to_strain_id[strain.display_name.lower()] = strain.id

    word = word.lower()
    return None if word not in word_to_strain_id else word_to_strain_id[word]

def get_strain_by_name(strain_name, to_ignore, nex_session):
    from src.sgd.model.nex.misc import Strain
    if strain_name not in to_ignore:
        try:
            int(strain_name)
        except ValueError:
            strain_id = get_word_to_strain_id(strain_name, nex_session)
            return None if strain_id is None else nex_session.query(Strain).filter_by(id=strain_id).first()
    return None

def link_strain_names(text, to_ignore, nex_session):
    words = text.split(' ')
    new_chunks = []
    chunk_start = 0
    i = 0
    for word in words:
        strain_name = word
        if strain_name.endswith('.') or strain_name.endswith(',') or strain_name.endswith('?') or strain_name.endswith('-'):
            strain_name = strain_name[:-1]
        if strain_name.endswith(')'):
            strain_name = strain_name[:-1]
        if strain_name.startswith('('):
            strain_name = strain_name[1:]


        strain = get_strain_by_name(strain_name.upper(), to_ignore, nex_session)

        if strain is not None:
            new_chunks.append(text[chunk_start: i])
            chunk_start = i + len(word) + 1

            new_chunk = "<a href='" + strain.link + "'>" + strain_name + "</a>"
            if word[-2] == ')':
                new_chunk = new_chunk + word[-2]
            if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-') or word.endswith(')'):
                new_chunk = new_chunk + word[-1]
            if word.startswith('('):
                new_chunk = word[0] + new_chunk
            new_chunks.append(new_chunk)
        i = i + len(word) + 1
    new_chunks.append(text[chunk_start: i])
    try:
        return ' '.join(new_chunks)
    except:
        print text
        return text
