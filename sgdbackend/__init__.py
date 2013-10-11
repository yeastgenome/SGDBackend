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

def get_bioent_from_request(request):
    from sgdbackend_utils.cache import get_cached_bioent
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, 'LOCUS')
    if bioent is None:
        raise Exception('Bioent could not be found.')
    return bioent
    
def get_ref_from_request(request):
    from sgdbackend_utils.cache import get_cached_reference
    identifier = request.matchdict['identifier']
    reference = get_cached_reference(identifier)
    if reference is None:
        raise Exception('Reference could not be found.')
    return reference

class SGDBackend(BackendInterface):
    def __init__(self, config):
        self.renderer = 'jsonp'
        
        engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)

        DBSession.configure(bind=engine)
        model_new_schema.Base.metadata.bind = engine
        config.add_renderer('jsonp', JSONP(param_name='callback'))

        from sgdbackend_utils.cache import cache_core
        cache_core()
        
    #Go
    def go_references(self, request):
        from sgdbackend.misc import make_references
        bioent = get_bioent_from_request(request)
        return make_references(['GO'], bioent['id'], only_primary=True)
    
    def go_enrichment(self, request):
        from sgdbackend import go
        bioent_format_names = request.json_body['bioent_format_names']
        return go.make_enrichment(bioent_format_names)
       
    #Interaction
    def interaction_overview(self, request):
        from sgdbackend import interaction
        bioent = get_bioent_from_request(request)
        return interaction.make_overview(bioent) 
    
    def interaction_details(self, request):
        from sgdbackend import interaction
        bioent = get_bioent_from_request(request) 
        return interaction.make_details(False, bioent['id']) 
        
    def interaction_graph(self, request):
        from sgdbackend import interaction
        bioent = get_bioent_from_request(request) 
        return interaction.make_graph(bioent['id'])
        
    def interaction_resources(self, request):
        from sgdbackend.misc import make_resources
        bioent = get_bioent_from_request(request)
        return make_resources('Interaction Resources', bioent['id'])
        
    def interaction_references(self, request):
        from sgdbackend.misc import make_references
        bioent = get_bioent_from_request(request)
        return make_references(['GENINTERACTION', 'PHYSINTERACTION'], bioent['id'])
       
    #Literature
    def literature_overview(self, request):
        from sgdbackend import literature
        bioent = get_bioent_from_request(request)
        return literature.make_overview(bioent['id'])

    def literature_details(self, request):
        from sgdbackend import literature
        bioent = get_bioent_from_request(request)
        return literature.make_details(bioent['id'])
    
    def literature_graph(self, request):
        from sgdbackend import literature
        bioent = get_bioent_from_request(request)
        return literature.make_graph(bioent['id'])
            
    #Phenotype
    def phenotype_references(self, request):
        from sgdbackend.misc import make_references
        bioent = get_bioent_from_request(request)
        return make_references(['PHENOTYPE'], bioent['id'], only_primary=True)
            
    #Protein
    def protein_domain_details(self, request):
        from sgdbackend import protein
        bioent = get_bioent_from_request(request)
        return protein.make_details(bioent['id'])
            
    #Regulation
    def regulation_overview(self, request):
        from sgdbackend import regulation
        bioent = get_bioent_from_request(request)
        return regulation.make_overview(bioent['id'])

    def regulation_details(self, request):
        from sgdbackend import regulation
        bioent = get_bioent_from_request(request)
        return regulation.make_details(True, bioent['id']) 
            
    def regulation_graph(self, request):
        from sgdbackend import regulation
        bioent = get_bioent_from_request(request)
        return regulation.make_graph(bioent['id'])

    def regulation_references(self, request):
        from sgdbackend.misc import make_references
        bioent = get_bioent_from_request(request)
        return make_references(['REGULATION'], bioent['id'])
      
    #Reference

    #Sequence
    def binding_site_details(self, request):
        from sgdbackend import sequence
        bioent = get_bioent_from_request(request)
        return sequence.make_details(bioent['id'])
            
    #Misc
    def bioentity(self, request):
        bioent = get_bioent_from_request(request)
        return bioent

    def bioentitytabs(self, request):
        from sgdbackend import misc
        bioent = get_bioent_from_request(request)
        return misc.make_bioentitytabs(bioent['id'])

    def all_bioents(self, request):
        from sgdbackend import misc
        min_id = None if 'min' not in request.GET else int(request.GET['min'])
        max_id = None if 'max' not in request.GET else int(request.GET['max'])
        return misc.make_all_bioents(min_id, max_id)

    def bioentity_list(self, request):
        from sgdbackend import misc
        bioent_ids = request.json_body['bioent_ids']
        return misc.make_bioent_list(bioent_ids)
    
    def reference(self, request):
        reference = get_bioent_from_request(request)
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

    
            
            
    
    