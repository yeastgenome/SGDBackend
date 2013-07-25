from config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE
from model_new_schema.link_maker import LinkMaker
from models import DBSession
from pyramid.config import Configurator
from pyramid.renderers import JSONP
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

    from go_enrichment import setup_go_enrichment_analysis    
    #setup_go_enrichment_analysis()

    return config

def prep_views(config):    
    #Search views
    config.add_route('search_results', '/search_results')
   
    #Bioent views
    config.add_route('bioent', '/bioent/{bioent_type}/{bioent}')
    config.add_route('all_bioents', '/all_bioents')
    config.add_route('locus', '/locus/{bioent}')
    config.add_route('bioent_overview_table', '/bioent_overview_table')
    config.add_route('bioent_evidence_table', '/bioent_evidence_table')
    
    #Biocon views
    config.add_route('biocon', '/biocon/{biocon_type}/{biocon}')

    #GO views
    config.add_route('go', '/go/{biocon}')
    config.add_route('go_evidence', '/go_evidence')
    config.add_route('go_overview_table', '/go_overview_table')
    config.add_route('go_evidence_table', '/go_evidence_table')
    config.add_route('go_graph', '/go_graph')
    config.add_route('go_ontology_graph', '/go_ontology_graph')
    
    #Phenotype views
    config.add_route('phenotype', '/phenotype/{biocon}')
    config.add_route('phenotype_evidence', '/phenotype_evidence')
    config.add_route('phenotype_overview_table', '/phenotype_overview_table')
    config.add_route('phenotype_evidence_table', '/phenotype_evidence_table')
    config.add_route('phenotype_graph', '/phenotype_graph')
    config.add_route('phenotype_ontology_graph', '/phenotype_ontology_graph')
            
    #Interaction views
    config.add_route('interaction_evidence', '/interaction_evidence')
    config.add_route('interaction_overview_table', '/interaction_overview_table')
    config.add_route('interaction_evidence_table', '/interaction_evidence_table')
    config.add_route('interaction_graph', '/interaction_graph') 
    config.add_route('interaction_evidence_resources', '/interaction_evidence_resources')
       
    #Reference views
    config.add_route('reference', '/reference/{reference}')
    config.add_route('reference_graph', '/reference_graph')
    config.add_route('author', '/author/{author}')
    config.add_route('assoc_references', '/assoc_references')

    #Chemical views    
    config.add_route('chemical', '/chemical/{chemical}')
    
    #Sequence views
    config.add_route('sequence', '/sequence')
    
    #List views
    config.add_route('list', '/list')
    config.add_route('go_enrichment', '/go_enrichment')


    config.scan()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = prep_sqlalchemy(**settings)
    prep_views(config)
    return config.make_wsgi_app()
