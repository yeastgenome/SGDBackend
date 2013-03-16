from .models import DBSession
from model_new_schema.bioentity import create_bioentity_subclasses
from pyramid.config import Configurator
from sgd2.config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import bioent_biocon_views
import bioent_views
import biorel_views
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
    
    config.add_route('home', '/')
    config.add_route('my_sgd', '/my_sgd')
    config.add_route('help', '/help')
    config.add_route('about', '/about')
    
    config.add_route('search', '/search/{search_str}')
    config.add_route('typeahead', '/typeahead')
   
    #Bioent views
    config.add_route('bioent', '/bioent/{bioent_name}')
    
    #GO views
    config.add_route('go', '/go/{biocon_name}')
    config.add_route('go_evidence', '/go_evidence')
    config.add_route('go_overview_table', '/go_overview_table')
    config.add_route('go_evidence_table', '/go_evidence_table')
    
    
    config.add_route('phenotype', '/phenotype/{biocon_name}')
        
    #Evidence views
    config.add_route('phenotype_evidence', '/phenotype_evidence')
    config.add_route('interaction_evidence', '/interaction_evidence')
    
    #Reference views
    config.add_route('reference', '/reference/{pubmed_id}')
    
    #Tables
    config.add_route('phenotype_overview_table', '/phenotype/overview_table')
    config.add_route('phenotype_evidence_table', '/phenotype/evidence_table')
    
    config.add_route('interaction_overview_table', '/interaction/overview_table')
    config.add_route('interaction_evidence_table', '/interaction/evidence_table')       
    
    config.add_route('bioent_all_biocon', '/bioent/{bioent_name}/biocon')
    config.add_route('bioent_go', '/bioent/{bioent_name}/go')
    config.add_route('bioent_phenotype', '/bioent/{bioent_name}/phenotype')
    config.add_route('bioent_interaction', '/bioent/{bioent_name}/interaction')

    config.add_route('bioent_all_biorel', '/bioent/{bioent_name}/biorel')
    config.add_route('bioent_interaction_graph', '/bioent/{bioent_name}/interaction_graph')
    config.add_route('bioent_go_graph', '/bioent/{bioent_name}/go_graph')

    config.add_route('biorel', '/biorel/{biorel_type}={biorel_name}')
    config.add_route('biorel_evidence', '/biorel/{biorel_type}={biorel_name}/evidence')
    
    config.add_route('biocon', '/biocon/{biocon_type}={biocon_name}')
    config.add_route('biocon_all_bioent', '/biocon/{biocon_type}={biocon_name}/bioent')
    
    config.add_route('bioent_biocon', '/bioent_biocon/{biocon_type}={bioent_biocon_name}')
    config.add_route('bioent_biocon_evidence', '/bioent_biocon/{biocon_type}={bioent_biocon_name}/evidence')

    config.add_route('reference_all_evidence', '/reference/{pubmed_id}/evidence')
    config.add_route('reference_phenotype', '/reference/{pubmed_id}/phenotype')
    config.add_route('reference_go', '/reference/{pubmed_id}/go')
    config.add_route('reference_interaction', '/reference/{pubmed_id}/interaction')
    
    config.add_route('allele', '/allele/{allele_name}')

    config.scan()
    return config.make_wsgi_app()
