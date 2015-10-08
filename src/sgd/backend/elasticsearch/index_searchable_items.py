from sqlalchemy import *
from src.sgd.convert import prepare_schema_connection
from src.sgd.convert import config
from src.sgd.model import nex
from src.sgd.model import perf
from elasticsearch import Elasticsearch

CLIENT_ADDRESS= 'http://localhost:9200'
INDEX_NAME = 'searchable_items'
DOC_TYPE = 'searchable_item'
RESET_INDEX = False
es = Elasticsearch(CLIENT_ADDRESS)

# prep session
nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, config.PERF_HOST, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.perf.core import Bioentity as PerfBioentity
from src.sgd.model.nex.reference import Author
from src.sgd.model.nex.misc import Strain
from src.sgd.model.nex.bioconcept import Go
nex_session = nex_session_maker()
perf_session = perf_session_maker()

def setup_index():
    exists = es.indices.exists(INDEX_NAME)
    if RESET_INDEX and exists:
        es.indices.delete(INDEX_NAME)
    exists = es.indices.exists(INDEX_NAME)
    if not exists:
        es.indices.create(INDEX_NAME)
        put_mapping()
    return

def put_mapping():
    return

def index_genes():
    print 'indexing genes'
    # get nex format of all genes
    all_genes = nex_session.query(Bioentity).all()
    for gene in all_genes:
        if gene.display_name == gene.format_name:
            _name = gene.display_name
        else:
            _name = gene.display_name + ' / ' + gene.format_name
        # get perf doc
        perf_result = perf_session.query(PerfBioentity).filter_by(id=gene.id).first()
        obj = {
            'name': _name,
            'href': gene.link,
            'description': gene.headline,
            'category': 'locus',
            'data': perf_result.to_json()
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=gene.sgdid)

def index_phenotypes():
    return

def index_authors():
    print 'indexing authors'
    # get nex format of all authors
    all_authors = nex_session.query(Author).all()
    for author in all_authors:
        obj = {
            'name': author.display_name,
            'href': author.link,
            'description': '',
            'category': 'author',
            'data': {}
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=author.id)

def index_strains():
    print 'indexing strains'
    all_strains = nex_session.query(Strain).all()
    for strain in all_strains:
        obj = {
            'name': strain.display_name,
            'href': strain.link,
            'description': strain.description,
            'category': 'strain',
            'data': {}
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=strain.id)

def index_go_terms():
    print 'indexing GO terms'
    all_gos = nex_session.query(Go).all()
    for go in all_gos:
        obj = {
            'name': go.display_name,
            'href': go.link,
            'description': go.description,
            'category': 'function',
            'data': {}
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=go.sgdid)

def main():
    setup_index()
    index_genes()
    index_phenotypes()
    index_authors()
    index_strains()
    index_go_terms()

    # experiments
    # pages

main()
