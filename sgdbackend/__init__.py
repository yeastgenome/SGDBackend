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
        config.add_renderer('jsonp', JSONP(param_name='callback'))

        from sgdbackend_utils.cache import cache_core
        cache_core()
        
    #Renderer
    def get_renderer(self, method_name):
        return 'jsonp'
    
    #Bioentity
    def all_bioentities(self, request):
        from sgdbackend import misc
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        return misc.make_all_bioentities(min_id, max_id)
    
    def bioentity_list(self, request):
        from sgdbackend import misc
        bioent_ids = request.json_body['bioent_ids']
        return misc.make_bioentity_list(bioent_ids)
    
    #Locus
    def locus(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_bioent
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        locus = None if locus_id is None else id_to_bioent[locus_id]
        return locus

    def locustabs(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import misc
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return misc.make_locustabs(locus_id)

    #Bioconcept
    def all_bioconcepts(self, request):
        from sgdbackend import misc
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        return misc.make_all_bioconcepts(min_id, max_id)
    
    def bioconcept_list(self, request):
        from sgdbackend import misc
        biocon_ids = request.json_body['biocon_ids']
        return misc.make_bioconcept_list(biocon_ids)
    
    #Reference
    def reference(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_reference
        identifier = request.matchdict['identifier']
        reference_id = get_obj_id(identifier, class_type='REFERENCE')
        reference = None if reference_id is None else id_to_reference[reference_id]
        return reference
       
    def all_references(self, request):
        from sgdbackend import misc
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        return misc.make_all_references(min_id, max_id)

    def all_bibentries(self, request):
        from sgdbackend import misc
        return misc.make_all_bibentries()

    def reference_list(self, request):
        from sgdbackend.misc import make_references
        reference_ids = request.json_body['reference_ids']
        make_references(reference_ids)
        
    #Go
    def go(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        identifier = request.matchdict['identifier']
        go_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        goterm = None if go_id is None else id_to_biocon[go_id]
        return goterm
    
    def go_references(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return make_references(['GO'], locus_id, only_primary=True)
    
    def go_enrichment(self, request):
        from sgdbackend import go
        bioent_format_names = request.json_body['bioent_format_names']
        return go.make_enrichment(bioent_format_names)
       
    #Interaction
    def interaction_overview(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_bioent
        from sgdbackend import interaction
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        locus = id_to_bioent[locus_id]
        return interaction.make_overview(locus) 
    
    def interaction_details(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import interaction
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return interaction.make_details(False, locus_id) 
        
    def interaction_graph(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import interaction
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return interaction.make_graph(locus_id)
        
    def interaction_resources(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_resources
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return make_resources('Interaction Resources', locus_id)
        
    def interaction_references(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return make_references(['GENINTERACTION', 'PHYSINTERACTION'], locus_id)
       
    #Literature
    def literature_overview(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import literature
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return literature.make_overview(locus_id)

    def literature_details(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import literature
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return literature.make_details(locus_id)
    
    def literature_graph(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import literature
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return literature.make_graph(locus_id)
            
    #Phenotype
    def phenotype(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        identifier = request.matchdict['identifier']
        pheno_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        phenotype = None if pheno_id is None else id_to_biocon[pheno_id]
        return phenotype
    
    def phenotype_references(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return make_references(['PHENOTYPE'], locus_id, only_primary=True)
            
    #Protein
    def protein_domain_details(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import protein
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return protein.make_details(locus_id)
            
    #Regulation
    def regulation_overview(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import regulation
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return regulation.make_overview(locus_id)

    def regulation_details(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import regulation
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return regulation.make_details(True, locus_id) 
            
    def regulation_graph(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import regulation
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return regulation.make_graph(locus_id)

    def regulation_references(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend.misc import make_references
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return make_references(['REGULATION'], locus_id)
      
    #Sequence
    def binding_site_details(self, request):
        from sgdbackend_query import get_obj_id
        from sgdbackend import sequence
        identifier = request.matchdict['identifier']
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        return sequence.make_details(locus_id)
    
    #Misc
    def all_disambigs(self, request):
        from sgdbackend import misc
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        return misc.make_all_disambigs(min_id, max_id)

    
            
            
    
    