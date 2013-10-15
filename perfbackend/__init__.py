from backend.backend_interface import BackendInterface
from config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE, SCHEMA
from go_enrichment import query_batter
from mpmath import ceil
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
import sys

# This class must implement BackendInterface, but it generates most of the methods with __getattr__.
class PerfBackend():
    def __init__(self, config):
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)
        self.meta = MetaData()
        self.meta.reflect(bind=self.engine)
        
    # Gets json for standard requests.
    def __getattr__(self, name):
        def f(request):
            locus_id = self.get_obj_id(request.matchdict['identifier'], subclass_type='LOCUS')
            table = self.meta.tables[name]
            result = self.engine.execute(select([table.c.json]).where(table.c.bioentity_id == locus_id)).fetchone()
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
    
    #Useful methods
    def get_obj_ids(self, identifier, class_type=None, subclass_type=None):
        disambig_table = self.meta.tables['disambig']
        query = select([disambig_table]).where(disambig_table.c.disambig_key == identifier.upper())
        if class_type is not None:
            query = query.where(disambig_table.c.class_type == class_type)
        if subclass_type is not None:
            query = query.where(disambig_table.c.subclass_type == subclass_type)
        disambigs = self.engine.execute(query).fetchall()
        
        if len(disambigs) > 0:
            return [(disambig.identifier, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
        return None
    
    def get_obj_id(self, identifier, class_type=None, subclass_type=None):
        objs_ids = self.get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
        obj_id = None if objs_ids is None or len(objs_ids) != 1 else objs_ids[0][0]
        return obj_id
    
    def get_obj(self, obj_table, id_column_name, identifier, class_type=None, subclass_type=None):
        obj_id = self.get_obj_id(identifier, class_type=class_type, subclass_type=subclass_type)
        
        if obj_id is not None:
            obj = self.engine.execute(select([obj_table]).where(getattr(obj_table.c, id_column_name) == obj_id)).fetchone()
            if obj is not None:
                return obj.json
        return None
    
    def get_all_objs(self, obj_table, id_column_name, min_id, max_id):
        query = select([obj_table])
        if min_id is not None:
            query = query.where(getattr(obj_table.c, id_column_name) >= min_id)
        if max_id is not None:
            query = query.where(getattr(obj_table.c, id_column_name) < max_id)
        objs = self.engine.execute(query).fetchall()
        return [obj.json for obj in objs]
    
    def get_obj_list(self, obj_table, id_column_name, obj_ids):
        objs = []
        
        batch_size = 500
        num_batches = int(ceil(1.0*len(obj_ids)/batch_size))
        for i in range(num_batches):
            new_obj_ids = obj_ids[i*batch_size:(i+1)*batch_size]
            new_objs = self.engine.execute(select([obj_table]).where(getattr(obj_table.c, id_column_name).in_(new_obj_ids))).fetchall()
            objs.extend([new_obj.json for new_obj in new_objs])

        return objs
    
    #Renderer
    def get_renderer(self, method_name):
        return 'string'
    
    #Bioentity
    def all_bioentities(self, request):
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        
        bioents = self.get_all_objs(self.meta.tables['bioentity'], 'bioentity_id', min_id, max_id)
        return '[' + ', '.join(bioents) + ']'
    
    def bioentity_list(self, request):
        bioent_ids = list(set(request.json_body['bioent_ids']))
        
        bioents = self.get_obj_list(self, self.meta.tables['bioentity'], 'bioentity_id', bioent_ids)
        return '[' + ', '.join(bioents) + ']'
    
    #Locus
    def locus(self, request):
        identifier = request.matchdict['identifier']
        bioent = self.get_obj(self.meta.tables['bioentity'], 'bioentity_id', identifier, class_type='BIOENTITY', subclass_type='LOCUS')
    
        if bioent is None:
            raise Exception('Locus could not be found.')
        return bioent
    
    def locustabs(self, request):
        identifier = request.matchdict['identifier']
        locustab = self.get_obj(self.meta.tables['locustabs'], 'bioentity_id', identifier, class_type='BIOENTITY', subclass_type='LOCUS')
    
        if locustab is None:
            raise Exception('Locustab could not be found.')
        return locustab
    
    #Bioconcept
    def all_bioconcepts(self, request):
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        
        biocons = self.get_all_objs(self.meta.tables['bioconcept'], 'bioconcept_id', min_id, max_id)
        return '[' + ', '.join(biocons) + ']'
    
    def bioconcept_list(self, request):
        biocon_ids = list(set(request.json_body['biocon_ids']))
        
        biocons = self.get_obj_list(self, self.meta.tables['bioconcept'], 'bioconcept_id', biocon_ids)
        return '[' + ', '.join(biocons) + ']'
     
    #Go
    def go(self, request):
        identifier = request.matchdict['identifier']
        biocon = self.get_obj(self.meta.tables['bioconcept'], 'bioconcept_id', identifier, class_type='BIOCONCEPT', subclass_type='GO')
    
        if biocon is None:
            raise Exception('Go term could not be found.')
        return biocon
    
    def go_enrichment(self, request):
        bioent_format_names = request.json_body['bioent_format_names']
        enrichment_results = query_batter.query_go_processes(bioent_format_names)
        json_format = []
        
        for enrichment_result in enrichment_results:
            identifier = str(int(enrichment_result[0][3:]))
            goterm = self.get_obj(self.meta.tables['bioconcept'], 'bioconcept_id', identifier, subclass_type='GO')
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        return json_format
    
    #Phenotype
    def phenotype(self, request):
        identifier = request.matchdict['identifier']
        biocon = self.get_obj(self.meta.tables['bioconcept'], 'bioconcept_id', identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
    
        if biocon is None:
            raise Exception('Go term could not be found.')
        return biocon
         
    #Reference
    def reference(self, request):
        identifier = request.matchdict['identifier']
        ref = self.get_obj(self.meta.tables['reference'], 'reference_id', identifier, class_type='REFERENCE')
    
        if ref is None:
            raise Exception('Reference could not be found.')
        return ref
       
    def all_references(self, request):
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        
        refs = self.get_all_objs(self.meta.tables['reference'], 'reference_id', min_id, max_id)
        return '[' + ', '.join(refs) + ']'
    
    def reference_list(self, request):
        ref_ids = list(set(request.json_body['reference_ids']))
        
        refs = self.get_obj_list(self.meta.tables['reference'], 'reference_id', ref_ids)
        return '[' + ', '.join(refs) + ']'

    def all_bibentries(self, request):
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        
        bibentries = self.get_all_objs(self.meta.tables['reference_bibentry'], 'reference_id', min_id, max_id)
        return '[' + ', '.join(bibentries) + ']'
    
    #Misc
    def all_disambigs(self, request):
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        
        disambigs = self.get_all_objs(self.meta.tables['disambig'], 'disambig_id', min_id, max_id)
        return '[' + ', '.join(disambigs) + ']'
    
    

    
            
            