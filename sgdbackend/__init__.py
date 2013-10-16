from backend.backend_interface import BackendInterface
from config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE, SCHEMA
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.response import Response
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import json
import model_new_schema
import sys

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
class Base(object):
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
model_new_schema.SCHEMA = SCHEMA
model_new_schema.Base = declarative_base(cls=Base)

class SGDBackend(BackendInterface):
    def __init__(self, config):
        engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)

        DBSession.configure(bind=engine)
        model_new_schema.Base.metadata.bind = engine

        from sgdbackend_utils.cache import cache_core
        cache_core()
        
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
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        from sgdbackend import misc
        return json.dumps(misc.make_all_bioentities(min_id, max_id))
    
    def bioentity_list(self, bioent_ids):
        from sgdbackend import misc
        return json.dumps(misc.make_bioentity_list(bioent_ids))
    
    #Locus
    def locus(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_bioent
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(id_to_bioent[locus_id])

    def locustabs(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import misc
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(misc.make_locustabs(locus_id))

    #Bioconcept
    def all_bioconcepts(self, min_id, max_id):
        from sgdbackend import misc
        return json.dumps(misc.make_all_bioconcepts(min_id, max_id))
    
    def bioconcept_list(self, biocon_ids):
        from sgdbackend import misc
        return json.dumps(misc.make_bioconcept_list(biocon_ids))
    
    #Reference
    def reference(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_reference
        reference_id = get_obj_id(identifier, class_type='REFERENCE')
        return None if reference_id is None else json.dumps(id_to_reference[reference_id])
       
    def all_references(self, min_id, max_id):
        from sgdbackend import misc
        return json.dumps(misc.make_all_references(min_id, max_id))

    def all_bibentries(self, min_id, max_id):
        from sgdbackend import misc
        return json.dumps(misc.make_all_bibentries(min_id, max_id))

    def reference_list(self, reference_ids):
        from sgdbackend import misc
        return json.dumps(misc.make_reference_list(reference_ids))
        
    #Go
    def go(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        go_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(id_to_biocon[go_id])
    
    def go_references(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(make_references(['GO'], locus_id, only_primary=True))
    
    def go_enrichment(self, bioent_format_names):
        from sgdbackend import go
        return json.dumps(go.make_enrichment(bioent_format_names))
       
    #Interaction
    def interaction_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_bioent
        from sgdbackend import interaction
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        locus = id_to_bioent[locus_id]
        return json.dumps(interaction.make_overview(locus)) 
    
    def interaction_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import interaction
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(interaction.make_details(False, locus_id))
        
    def interaction_graph(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import interaction
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(interaction.make_graph(locus_id))
        
    def interaction_resources(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_resources
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(make_resources('Interaction Resources', locus_id))
        
    def interaction_references(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(make_references(['GENINTERACTION', 'PHYSINTERACTION'], locus_id))
       
    #Literature
    def literature_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import literature
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(literature.make_overview(locus_id))

    def literature_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import literature
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(literature.make_details(locus_id))
    
    def literature_graph(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import literature
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(literature.make_graph(locus_id))
            
    #Phenotype
    def phenotype(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        pheno_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return None if pheno_id is None else json.dumps(id_to_biocon[pheno_id])
    
    def phenotype_references(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(make_references(['PHENOTYPE'], locus_id, only_primary=True))
            
    #Protein
    def protein_domain_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import protein
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(protein.make_details(locus_id))
            
    #Regulation
    def regulation_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import regulation
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(regulation.make_overview(locus_id))

    def regulation_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import regulation
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(regulation.make_details(True, locus_id))
            
    def regulation_graph(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import regulation
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(regulation.make_graph(locus_id))

    def regulation_references(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(make_references(['REGULATION'], locus_id))
      
    #Sequence
    def binding_site_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import sequence
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(sequence.make_details(locus_id))
    
    #Misc
    def all_disambigs(self, min_id, max_id):
        from sgdbackend import misc
        return json.dumps(misc.make_all_disambigs(min_id, max_id))

    
            
            
    
    