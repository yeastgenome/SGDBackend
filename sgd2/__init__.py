from .models import DBSession
from model_new_schema.bioentity import create_bioentity_subclasses
from model_new_schema.link_maker import LinkMaker
from pyramid.config import Configurator
from sgd2.config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import model_new_schema

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)

    DBSession.configure(bind=engine)
    model_new_schema.Base.metadata.bind = engine
    create_bioentity_subclasses(DBSession)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    #Basic views
    config.add_route('home', '/')
    config.add_route('my_sgd', '/my_sgd')
    config.add_route('help', '/help')
    config.add_route('about', '/about')
    
    #Search views
    config.add_route('search', '/search/{search_str}')
    config.add_route('typeahead', '/typeahead')
   
    #Bioent views
    config.add_route('bioent', '/bioent/{bioent_name}')
    
    #GO views
    config.add_route('go', '/go/{biocon_name}')
    config.add_route('go_evidence', '/go_evidence')
    config.add_route('go_overview_table', '/go_overview_table')
    config.add_route('go_evidence_table', '/go_evidence_table')
    config.add_route('go_graph', '/go_graph')
    
    #Phenotype views
    config.add_route('phenotype', '/phenotype/{biocon_name}')
    config.add_route('phenotype_evidence', '/phenotype_evidence')
    config.add_route('phenotype_overview_table', '/phenotype_overview_table')
    config.add_route('phenotype_evidence_table', '/phenotype_evidence_table')
    config.add_route('phenotype_graph', '/phenotype_graph')
            
    #Interaction views
    config.add_route('interaction_evidence', '/interaction_evidence')
    config.add_route('interaction_overview_table', '/interaction_overview_table')
    config.add_route('interaction_evidence_table', '/interaction_evidence_table')
    config.add_route('interaction_graph', '/interaction_graph') 
       
    #Reference views
    config.add_route('reference', '/reference/{pubmed_id}')

    config.scan()
    return config.make_wsgi_app()
