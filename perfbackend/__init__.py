from backend.backend_interface import BackendInterface
from datetime import datetime
from go_enrichment import query_batter
from model_perf_schema.data import create_data_classes, data_classes
from mpmath import ceil
from perfbackend_utils import set_up_logging
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.response import Response
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import select
from zope.sqlalchemy import ZopeTransactionExtension
import json
import logging
import model_perf_schema
import sys
import uuid

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class PerfBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}
                
        model_perf_schema.SCHEMA = schema
        model_perf_schema.Base = declarative_base(cls=Base)

        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), convert_unicode=True, pool_recycle=3600)

        DBSession.configure(bind=engine)
        model_perf_schema.Base.metadata.bind = engine

        create_data_classes()
        
        self.log = set_up_logging(log_directory, 'perfbackend')
        
    #Renderer
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name, request):
        request_id = str(uuid.uuid4())
        callback = None if 'callback' not in request.GET else request.GET['callback']
        self.log.info(request_id + ' ' + method_name + ('' if 'identifier' not in request.matchdict else ' ' + request.matchdict['identifier']))
        def f(data):
            self.log.info(request_id + ' end')
            if callback is not None:
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        from model_perf_schema.core import Bioentity
        return get_all(Bioentity, 'json', min_id, max_id)
    
    def bioentity_list(self, bioent_ids):
        from model_perf_schema.core import Bioentity
        return get_list(Bioentity, 'json', bioent_ids)
    
    #Locus
    def locus(self, identifier):
        from model_perf_schema.core import Bioentity
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_obj(Bioentity, 'json', bioent_id)
    
    def locustabs(self, identifier):
        from model_perf_schema.core import Bioentity
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_obj(Bioentity, 'locustabs_json', bioent_id)
    
    def all_locustabs(self, min_id, max_id):
        from model_perf_schema.core import Bioentity
        return get_all(Bioentity, 'locustabs_json', min_id, max_id)
    
    #Bioconcept
    def all_bioconcepts(self, min_id, max_id, callback=None):
        from model_perf_schema.core import Bioconcept
        return get_all(Bioconcept, 'json', min_id, max_id)
    
    def bioconcept_list(self, biocon_ids, callback=None):
        from model_perf_schema.core import Bioconcept
        return get_list(Bioconcept, 'json', biocon_ids)
    
    #Reference
    def reference(self, identifier):
        from model_perf_schema.core import Reference
        ref_id = get_obj_id(identifier, class_type='REFERENCE')
        return get_obj(Reference, 'json', ref_id)
       
    def all_references(self, min_id, max_id):
        from model_perf_schema.core import Reference
        return get_all(Reference, 'json', min_id, max_id)

    def all_bibentries(self, min_id, max_id):
        from model_perf_schema.core import Reference
        return get_all(Reference, 'bibentry_json', min_id, max_id)
    
    def reference_list(self, reference_ids):
        from model_perf_schema.core import Reference
        return get_list(Reference, 'bibentry_json', reference_ids)
    
    #Interaction
    def interaction_overview(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('interaction_overview', bioent_id)
    
    def interaction_details(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('interaction_details', bioent_id)
    
    def interaction_graph(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('interaction_graph', bioent_id)
    
    def interaction_resources(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('interaction_resources', bioent_id)
    
    #Literature
    def literature_overview(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('literature_overview', bioent_id)
    
    def literature_details(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('literature_details', bioent_id)
    
    def literature_graph(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('literature_graph', bioent_id)
    
    def go_enrichment(self, bioent_ids, callback=None):
        from model_perf_schema.core import Bioentity, Bioconcept
        bioent_format_names = []
        num_chunks = ceil(1.0*len(bioent_ids)/500)
        for i in range(num_chunks):
            bioent_format_names.extend([json.loads(x.json)['format_name'] for x in DBSession.query(Bioentity).filter(Bioentity.id.in_(bioent_ids[i*500:(i+1)*500])).all()])
        enrichment_results = query_batter.query_go_processes(bioent_format_names)
        json_format = []
        
        for enrichment_result in enrichment_results:
            identifier = 'GO:' + str(int(enrichment_result[0][3:]))
            goterm_id = get_obj_id(identifier, 'BIOCONCEPT', 'GO')
            goterm = json.loads(get_obj(Bioconcept, 'json', goterm_id))
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        return json.dumps(json_format)
    
    #Protein
    def protein_domain_details(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('protein_domain_details', bioent_id)
    
    def regulation_overview(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('regulation_overview', bioent_id)
    
    def regulation_details(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('regulation_details', bioent_id)
    
    def regulation_graph(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('regulation_graph', bioent_id)
    
    def regulation_target_enrichment(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('regulation_target_enrich', bioent_id)
    
    #Binding
    def binding_site_details(self, identifier):
        bioent_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return get_data('binding_site_details', bioent_id)

    #Misc
    def all_disambigs(self, min_id, max_id):
        from model_perf_schema.core import Disambig
        query = DBSession.query(Disambig)
        if min_id is not None:
            query = query.filter(Disambig.id >= min_id)
        if max_id is not None:
            query = query.filter(Disambig.id < max_id)
        disambigs = query.all()
        return json.dumps([{'id': disambig.id,
                            'disambig_key': disambig.disambig_key,
                            'class_type': disambig.class_type,
                            'subclass_type': disambig.subclass_type,
                            'identifier': disambig.obj_id} 
                        for disambig in disambigs]) 
        
#Useful methods
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    from model_perf_schema.core import Disambig
    
    if identifier is None:
        return None
    query = DBSession.query(Disambig).filter(Disambig.disambig_key==str(identifier).upper())
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    if len(disambigs) > 0:
        return [(disambig.obj_id, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
    return None

def get_obj_id(identifier, class_type=None, subclass_type=None):
    objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
    obj_id = None if objs_ids is None or len(objs_ids) != 1 else objs_ids[0][0]
    return obj_id

def get_all(cls, col_name, min_id, max_id):
    query = DBSession.query(cls)
    if min_id is not None:
        query = query.filter(cls.id >= min_id)
    if max_id is not None:
        query = query.filter(cls.id < max_id)
    objs = query.all()
        
    return '[' + ', '.join(filter(None, [getattr(obj, col_name) for obj in objs])) + ']'

def get_list(cls, col_name, obj_ids):
    num_chunks = ceil(1.0*len(obj_ids)/500)
    objs = []
    for i in range(num_chunks):
        objs.extend(DBSession.query(cls).filter(cls.id.in_(obj_ids[i*500:(i+1)*500])).all())
    return '[' + ', '.join([getattr(obj, col_name) for obj in objs]) + ']'
            
def get_obj(cls, col_name, obj_id):
    if obj_id is not None:
        biocon = DBSession.query(cls).filter(cls.id == obj_id).first()
        return None if biocon is None else getattr(biocon, col_name)
    return None

def get_data(table_name, obj_id):
    if obj_id is not None:
        data_cls = data_classes[table_name]
        data = DBSession.query(data_cls).filter(data_cls.id == obj_id).first()
        return None if data is None else data.json
    return None
        
            