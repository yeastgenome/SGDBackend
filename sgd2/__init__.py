from .models import DBSession
from model_new_schema.bioentity import create_bioentity_subclasses
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
    
    config.add_route('home', '/')
    config.add_route('my_sgd', '/my_sgd')
    config.add_route('help', '/help')
    config.add_route('about', '/about')
    
    config.add_route('search', '/search/{search_str}')
    config.add_route('typeahead', '/typeahead')
   
    config.add_route('bioent', '/bioent/{bioent_name}')
    config.add_route('bioent_phenotypes', '/bioent/{bioent_name}/phenotypes')
    config.add_route('bioent_interactions', '/bioent/{bioent_name}/interactions')
    config.add_route('bioent_interactions2', '/bioent/{bioent_name}/interactions2')
    config.add_route('bioent_interactions3', '/bioent/{bioent_name}/interactions3')

    config.add_route('bioent_graph', '/bioent_graph/{bioent_name}')

    config.add_route('biorel', '/biorel/{biorel_name}')
    config.add_route('biorel_genetic_evidence', '/biorel/{biorel_name}/genetic_evidence')
    config.add_route('biorel_physical_evidence', '/biorel/{biorel_name}/physical_evidence')
    config.add_route('biorel_references', '/biorel/{biorel_name}/references')
    
    config.add_route('biocon', '/biocon/{biocon_name}')
    config.add_route('biocon_genes', '/biocon/{biocon_name}/genes')
    
    config.add_route('bioent_biocon', '/bioent_biocon/{bioent_biocon_name}')
    config.add_route('bioent_biocon_references', '/bioent_biocon/{bioent_biocon_name}/references')
    config.add_route('bioent_biocon_evidence', '/bioent_biocon/{bioent_biocon_name}/evidence')

    config.add_route('reference', '/reference/{pubmed_id}')
    config.add_route('reference_phenotypes', '/reference/{pubmed_id}/phenotypes')
    config.add_route('reference_interactions', '/reference/{pubmed_id}/interactions')
    
    config.add_route('evidence', '/evidence/{evidence_id}')
    config.add_route('allele', '/allele/{allele_name}')

    config.scan()
    return config.make_wsgi_app()
