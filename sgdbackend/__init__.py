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
import uuid

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
class Base(object):
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
model_new_schema.SCHEMA = SCHEMA
model_new_schema.Base = declarative_base(cls=Base)

class SGDBackend(BackendInterface):
    def __init__(self, config):
        engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), pool_recycle=3600)

        DBSession.configure(bind=engine)
        model_new_schema.Base.metadata.bind = engine

        from sgdbackend_utils.cache import cache_core
        cache_core()
        
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name):
        request_id = uuid.uuid4()
        #log request start
        def f(data, request):
            #log request end
            callback = None if 'callback' not in request.GET else request.GET['callback']
            if callback is not None:
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        from sgdbackend_utils.cache import id_to_bioent
        return json.dumps([value for key, value in id_to_bioent.iteritems() if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])
    
    def bioentity_list(self, bioent_ids):
        from sgdbackend_utils.cache import id_to_bioent
        return json.dumps([id_to_bioent[x] for x in bioent_ids])
    
    #Locus
    def locus(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_bioent
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(id_to_bioent[locus_id])

    def locustabs(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_query.query_auxiliary import query_locustabs
        from sgdbackend_utils.obj_to_json import locustab_to_json
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(locustab_to_json(query_locustabs(locus_id)))

    #Bioconcept
    def all_bioconcepts(self, min_id, max_id):
        from sgdbackend_utils.cache import id_to_biocon
        return json.dumps([value for key, value in id_to_biocon.iteritems() if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])
    
    def bioconcept_list(self, biocon_ids):
        from sgdbackend_utils.cache import id_to_biocon
        return json.dumps([id_to_biocon[x] for x in biocon_ids])
    
    #Reference
    def reference(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_reference
        reference_id = get_obj_id(identifier, class_type='REFERENCE')
        return None if reference_id is None else json.dumps(id_to_reference[reference_id])
       
    def all_references(self, min_id, max_id):
        from sgdbackend_utils.cache import id_to_reference
        return json.dumps([value for key, value in id_to_reference.iteritems() if (min_id is None or key >= min_id) and (max_id is None or key < max_id)])
    
    def all_bibentries(self, min_id, max_id):
        from sgdbackend_query.query_reference import get_reference_bibs
        return json.dumps([{'id': x.id, 'text': x.text} for x in get_reference_bibs(min_id=min_id, max_id=max_id)])

    def reference_list(self, reference_ids):
        from sgdbackend_query.query_reference import get_reference_bibs
        return json.dumps([{'id': x.id, 'text': x.text} for x in get_reference_bibs(reference_ids=reference_ids)])
        
    #Go
    def go(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        go_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(id_to_biocon[go_id])
    
    def go_ontology(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        go_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None
    
    def go_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_go
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_go.make_overview(locus_id))
    
    def go_details(self, locus_identifier=None, go_identifier=None):
        print locus_identifier, go_identifier
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_go
        locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        go_id = None if go_identifier is None else get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return json.dumps(view_go.make_details(locus_id=locus_id, go_id=go_id))
    
    def go_enrichment(self, bioent_ids):
        from sgdbackend import view_go
        return json.dumps(view_go.make_enrichment(bioent_ids))
       
    #Interaction
    def interaction_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_bioent
        from sgdbackend import view_interaction
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        if locus_id is None:
            return None
        locus = id_to_bioent[locus_id]
        return json.dumps(view_interaction.make_overview(locus)) 
    
    def interaction_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_interaction
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_interaction.make_details(False, locus_id))
        
    def interaction_graph(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_interaction
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_interaction.make_graph(locus_id))
        
    def interaction_resources(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_query.query_misc import get_urls
        from sgdbackend_utils.obj_to_json import url_to_json
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        print locus_id
        resources = get_urls('Interaction Resources', bioent_id=locus_id)
        resources.sort(key=lambda x: x.display_name)
        return json.dumps([url_to_json(url) for url in resources])
       
    #Literature
    def literature_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_literature
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_literature.make_overview(locus_id))

    def literature_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_literature
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_literature.make_details(locus_id))
    
    def literature_graph(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_literature
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_literature.make_graph(locus_id))
            
    #Phenotype
    def phenotype(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        pheno_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return None if pheno_id is None else json.dumps(id_to_biocon[pheno_id])

    def phenotype_ontology(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend_utils.cache import id_to_biocon
        pheno_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return None
        
    def phenotype_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_phenotype.make_overview(locus_id))
    
    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_phenotype
        locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        phenotype_id = None if phenotype_identifier is None else get_obj_id(phenotype_identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return json.dumps(view_phenotype.make_details(locus_id=locus_id, phenotype_id=phenotype_id))
            
    #Protein
    def protein_domain_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_protein
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_protein.make_details(locus_id))
            
    #Regulation
    def regulation_overview(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_overview(locus_id))

    def regulation_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_details(True, locus_id))
            
    def regulation_graph(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_regulation
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_graph(locus_id))
      
    #Binding
    def binding_site_details(self, identifier):
        from sgdbackend_query import get_obj_id
        from sgdbackend import view_binding
        locus_id = get_obj_id(identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_binding.make_details(locus_id))
    
    #Misc
    def all_disambigs(self, min_id, max_id):
        from sgdbackend_query.query_auxiliary import get_disambigs
        from sgdbackend_utils.obj_to_json import disambig_to_json
        return json.dumps([disambig_to_json[x] for x in get_disambigs(min_id, max_id)])

    
            
            
    
    