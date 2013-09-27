from config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE
from models import DBSession
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from sgdbackend.cache import cache_core
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import model_new_schema

def prep_sqlalchemy(**settings):
    engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)

    DBSession.configure(bind=engine)
    model_new_schema.Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    cache_core()

    return config

def prep_views(config):    
    
    #Reference views
    config.add_route('all_references', '/all_references')
    config.add_route('reference', '/reference/{identifier}/overview')
    config.add_route('reference_list', '/reference_list')
    
    #Bioent views
    config.add_route('bioentity', '/{type}/{identifier}/overview')
    config.add_route('all_bioents', '/all_bioents')
    
    #Interaction views
    config.add_route('interaction_overview', '/{type}/{identifier}/interaction_overview')
    config.add_route('interaction_details', '/{type}/{identifier}/interaction_details')
    config.add_route('interaction_graph', '/{type}/{identifier}/interaction_graph') 
    config.add_route('interaction_resources', '/{type}/{identifier}/interaction_resources')
    config.add_route('interaction_references', '/{type}/{identifier}/interaction_references')
    
    #Regulation views
    config.add_route('regulation_overview', '/{type}/{identifier}/regulation_overview')
    config.add_route('regulation_details', '/{type}/{identifier}/regulation_details')
    config.add_route('regulation_graph', '/{type}/{identifier}/regulation_graph')
    config.add_route('regulation_references', '/{type}/{identifier}/regulation_references')
    
    #Literature views
    config.add_route('literature_overview', '/{type}/{identifier}/literature_overview')
    config.add_route('literature_details', '/{type}/{identifier}/literature_details')
    config.add_route('literature_graph', '/{type}/{identifier}/literature_graph')
    
    #Protein views
    config.add_route('protein_domain_details', '/{type}/{identifier}/protein_domain_details')

    config.add_route('binding_site_details', '/{type}/{identifier}/binding_site_details')
#    #Biocon views
#    config.add_route('biocon', '/biocon/{biocon_type}/{biocon}')
#
    #GO views
    config.add_route('go_references', '/{type}/{identifier}/go_references')
#    config.add_route('go', '/go/{biocon}')
#    config.add_route('go_evidence', '/go_evidence')
#    config.add_route('go_overview_table', '/go_overview_table')
#    config.add_route('go_evidence_table', '/go_evidence_table')
#    config.add_route('go_graph', '/go_graph')
#    config.add_route('go_ontology_graph', '/go_ontology_graph')
#    
    #Phenotype views
    config.add_route('phenotype_references', '/{type}/{identifier}/phenotype_references')
#    config.add_route('phenotype', '/phenotype/{biocon}')
#    config.add_route('phenotype_evidence', '/phenotype_evidence')
#    config.add_route('phenotype_overview_table', '/phenotype_overview_table')
#    config.add_route('phenotype_evidence_table', '/phenotype_evidence_table')
#    config.add_route('phenotype_graph', '/phenotype_graph')
#    config.add_route('phenotype_ontology_graph', '/phenotype_ontology_graph')
#       
#    #Reference views
#    config.add_route('reference', '/reference/{reference}')
#    config.add_route('reference_graph', '/reference_graph')
#    config.add_route('author', '/author/{author}')
#    config.add_route('assoc_references', '/assoc_references')
    
    #List views
    config.add_route('bioent_list', '/bioent_list')
    #config.add_route('go_enrichment', '/go_enrichment')


    config.scan()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = prep_sqlalchemy(**settings)
    prep_views(config)
    return config.make_wsgi_app()
