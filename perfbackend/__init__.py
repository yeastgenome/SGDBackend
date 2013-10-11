from backend.backend_interface import BackendInterface
from config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE, SCHEMA
from perfbackend_utils.cache import get_bioent_id, id_to_bioent, \
    get_cached_bioent
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.response import Response
from sgdbackend_query.query_reference import get_reference_bibs
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import select
from zope.sqlalchemy import ZopeTransactionExtension
import json
import sys

def get_bioent_id_from_request(request):
    from perfbackend_utils.cache import get_cached_bioent
    identifier = request.matchdict['identifier']
    bioent_id = get_bioent_id(identifier, 'LOCUS')
    if bioent_id is None:
        raise Exception('Bioent could not be found.')
    return bioent_id

class PerfBackend():
    def __init__(self, config):
        self.renderer = 'string'
        
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)
        self.meta = MetaData()
        self.meta.reflect(bind=self.engine)

        config.add_renderer('jsonp', JSONP(param_name='callback'))

        from perfbackend_utils.cache import cache_core
        cache_core(self.engine, self.meta)
        
    def __getattr__(self, name):
        def f(request):
            bioent_id = get_bioent_id_from_request(request)
            table = self.meta.tables[name]
            result = self.engine.execute(select([table.c.json]).where(table.c.bioentity_id == bioent_id)).fetchone()
            if result is not None:
                result = result[0]
            
            if result is None:
                return Response(status_int=500, body= 'Data could not be found.')
            if 'callback' in request.GET:
                callback = request.GET['callback']
                return Response(body="%s(%s)" % (callback, result), content_type='application/json')
            else:
                return Response(body=result, content_type='application/json')
        return f
        
#    #Go
#    def go_enrichment(self, request):
#        pass
            
    #Misc
    def bioentity(self, request):
        identifier = request.matchdict['identifier']
        bioent = get_cached_bioent(identifier, 'LOCUS')
        if bioent is None:
            raise Exception('Bioent could not be found.')
        return bioent
    
    def all_bioents(self, request):
        min_id = None
        max_id = None
        if 'min' in request.GET and 'max' in request.GET:
            min_id = int(request.GET['min'])
            max_id = int(request.GET['max'])
        bioents = {}
        for bioent in id_to_bioent.values():
            bioent_id = bioent['id']
            if min_id is not None:
                if bioent_id >= min_id and bioent_id < max_id:
                    bioents[bioent_id] = bioent
            else:
                bioents[bioent_id] = bioent
        return bioents.values()

    def bioentity_list(self, request):
        bioent_ids = request.json_body['bioent_ids']
        bioents = []
        for bioent_id in bioent_ids:
            bioent = get_cached_bioent(str(bioent_id), bioent_type='LOCUS')
            if bioent is not None:
                bioents.append(json.loads(bioent))
        return bioents
    
    def reference(self, request):
        pass
       
    def all_references(self, request):
        pass

    def all_bibentries(self, request):
        pass

    def reference_list(self, request):
        reference_ids = request.json_body['reference_ids']
        ref_bibs = get_reference_bibs(reference_ids=reference_ids)
        if ref_bibs is None:
            return Response(status_int=500, body='References could not be found.')
        
        return ref_bibs 
            
            