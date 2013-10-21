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
        engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), pool_recycle=3600)
        self.session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        self.session.configure(bind=engine)
        self.meta = MetaData()
        self.meta.reflect(bind=engine)
        
    #Renderer
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name):
        def f(data, request):
            callback = None if 'callback' not in request.GET else request.GET['callback']
            if callback is not None:
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f
            
    # Gets json for standard requests.
    def __getattr__(self, name):
        def f(identifier):
            locus_id = self.get_obj_id(identifier, subclass_type='LOCUS')
            table = self.meta.tables[name]
            result = self.session.query(select([table.c.json]).where(table.c.bioentity_id == locus_id)).first()
            if result is not None:
                result = result[0]
            return result
        return f
    
    #Useful methods
    def get_obj_ids(self, identifier, class_type=None, subclass_type=None):
        disambig_table = self.meta.tables['disambig']
        query = select([disambig_table]).where(disambig_table.c.disambig_key == identifier.upper())
        if class_type is not None:
            query = query.where(disambig_table.c.class_type == class_type)
        if subclass_type is not None:
            query = query.where(disambig_table.c.subclass_type == subclass_type)
        disambigs = self.session.query(query).all()
        
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
            obj = self.session.query(select([obj_table]).where(getattr(obj_table.c, id_column_name) == obj_id)).first()
            if obj is not None:
                return obj.json
        return None
    
    def get_all_objs(self, obj_table, id_column_name, min_id, max_id):
        query = select([obj_table])
        if min_id is not None:
            query = query.where(getattr(obj_table.c, id_column_name) >= min_id)
        if max_id is not None:
            query = query.where(getattr(obj_table.c, id_column_name) < max_id)
        objs = self.session.query(query).all()
        return [obj.json for obj in objs]
    
    def get_obj_list(self, obj_table, id_column_name, obj_ids):
        objs = []
        
        batch_size = 500
        num_batches = int(ceil(1.0*len(obj_ids)/batch_size))
        for i in range(num_batches):
            new_obj_ids = obj_ids[i*batch_size:(i+1)*batch_size]
            new_objs = self.session.query(select([obj_table]).where(getattr(obj_table.c, id_column_name).in_(new_obj_ids))).all()
            objs.extend([new_obj.json for new_obj in new_objs])

        return objs
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        bioents = self.get_all_objs(self.meta.tables['bioentity'], 'bioentity_id', min_id, max_id)
        return '[' + ', '.join(bioents) + ']'
    
    def bioentity_list(self, bioent_ids):
        bioents = self.get_obj_list(self.meta.tables['bioentity'], 'bioentity_id', bioent_ids)
        return '[' + ', '.join(bioents) + ']'
    
    #Locus
    def locus(self, identifier):
        bioent = self.get_obj(self.meta.tables['bioentity'], 'bioentity_id', identifier, class_type='BIOENTITY', subclass_type='LOCUS')
    
        if bioent is None:
            raise Exception('Locus could not be found.')
        return bioent
    
    def locustabs(self, identifier):
        locustab = self.get_obj(self.meta.tables['locustabs'], 'bioentity_id', identifier, class_type='BIOENTITY', subclass_type='LOCUS')
    
        if locustab is None:
            raise Exception('Locustab could not be found.')
        return locustab
    
    #Bioconcept
    def all_bioconcepts(self, min_id, max_id):
        biocons = self.get_all_objs(self.meta.tables['bioconcept'], 'bioconcept_id', min_id, max_id)
        return '[' + ', '.join(biocons) + ']'
    
    def bioconcept_list(self, biocon_ids):
        biocon_ids = list(set(biocon_ids))
        
        biocons = self.get_obj_list(self.meta.tables['bioconcept'], 'bioconcept_id', biocon_ids)
        return '[' + ', '.join(biocons) + ']'
     
    #Go
    def go(self, identifier):
        biocon = self.get_obj(self.meta.tables['bioconcept'], 'bioconcept_id', identifier, class_type='BIOCONCEPT', subclass_type='GO')
    
        if biocon is None:
            raise Exception('Go term could not be found.')
        return biocon
    
    def go_enrichment(self, bioent_ids):
        bioent_format_names = [json.loads(bioent)['format_name'] for bioent in self.get_obj_list(self.meta.tables['bioentity'], 'bioentity_id', bioent_ids)]
        enrichment_results = query_batter.query_go_processes(bioent_format_names)
        json_format = []
        for enrichment_result in enrichment_results:
            identifier = str(int(enrichment_result[0][3:]))
            goterm = json.loads(self.get_obj(self.meta.tables['bioconcept'], 'bioconcept_id', identifier, class_type='BIOCONCEPT', subclass_type='GO'))
            json_format.append({'go': goterm,
                                'match_count': enrichment_result[1],
                                'pvalue': enrichment_result[2]})
        return json.dumps(json_format)
    
    #Phenotype
    def phenotype(self, identifier):
        biocon = self.get_obj(self.meta.tables['bioconcept'], 'bioconcept_id', identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
    
        if biocon is None:
            raise Exception('Phenotype could not be found.')
        return biocon
         
    #Reference
    def reference(self, identifier):
        ref = self.get_obj(self.meta.tables['reference'], 'reference_id', identifier, class_type='REFERENCE')
    
        if ref is None:
            raise Exception('Reference could not be found.')
        return ref
       
    def all_references(self, min_id, max_id):
        refs = self.get_all_objs(self.meta.tables['reference'], 'reference_id', min_id, max_id)
        return '[' + ', '.join(refs) + ']'
    
    def reference_list(self, reference_ids):
        refs = self.get_obj_list(self.meta.tables['reference'], 'reference_id', reference_ids)
        return '[' + ', '.join(refs) + ']'

    def all_bibentries(self, min_id, max_id):
        bibentries = self.get_all_objs(self.meta.tables['reference_bibentry'], 'reference_id', min_id, max_id)
        return '[' + ', '.join(bibentries) + ']'
    
    #Misc
    def all_disambigs(self, min_id, max_id):
        disambigs = self.get_all_objs(self.meta.tables['disambig'], 'disambig_id', min_id, max_id)
        return '[' + ', '.join(disambigs) + ']'
    
    

    
            
            