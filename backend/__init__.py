from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import sys

def prep_views(chosen_backend, config):  
    
    renderer = chosen_backend.renderer  
    
    #Reference views
    config.add_route('all_references', '/all_references', view=getattr(chosen_backend, 'all_references'), renderer=renderer)
    config.add_route('all_bibentries', '/all_bibentries', view=getattr(chosen_backend, 'all_bibentries'), renderer=renderer)
    config.add_route('reference', '/reference/{identifier}/overview', view=getattr(chosen_backend, 'reference'), renderer=renderer)
    
    #Bioent views
    config.add_route('bioentity', '/locus/{identifier}/overview', view=getattr(chosen_backend, 'bioentity'), renderer=renderer)
    config.add_route('all_bioents', '/all_bioents', view=getattr(chosen_backend, 'all_bioents'), renderer=renderer)
    config.add_route('bioentitytabs', '/locus/{identifier}/tabs', view=getattr(chosen_backend, 'bioentitytabs'), renderer=renderer)
    
    #Interaction views
    config.add_route('interaction_overview', '/locus/{identifier}/interaction_overview', view=getattr(chosen_backend, 'interaction_overview'), renderer=renderer)
    config.add_route('interaction_details', '/locus/{identifier}/interaction_details', view=getattr(chosen_backend, 'interaction_details'), renderer=renderer)
    config.add_route('interaction_graph', '/locus/{identifier}/interaction_graph', view=getattr(chosen_backend, 'interaction_graph'), renderer=renderer)
    config.add_route('interaction_resources', '/locus/{identifier}/interaction_resources', view=getattr(chosen_backend, 'interaction_resources'), renderer=renderer)
    config.add_route('interaction_references', '/locus/{identifier}/interaction_references', view=getattr(chosen_backend, 'interaction_references'), renderer=renderer)
    
    #Regulation views
    config.add_route('regulation_overview', '/locus/{identifier}/regulation_overview', view=getattr(chosen_backend, 'regulation_overview'), renderer=renderer)
    config.add_route('regulation_details', '/locus/{identifier}/regulation_details', view=getattr(chosen_backend, 'regulation_details'), renderer=renderer)
    config.add_route('regulation_graph', '/locus/{identifier}/regulation_graph', view=getattr(chosen_backend, 'regulation_graph'), renderer=renderer)
    config.add_route('regulation_references', '/locus/{identifier}/regulation_references', view=getattr(chosen_backend, 'regulation_references'), renderer=renderer)
    
    #Literature views
    config.add_route('literature_overview', '/locus/{identifier}/literature_overview', view=getattr(chosen_backend, 'literature_overview'), renderer=renderer)
    config.add_route('literature_details', '/locus/{identifier}/literature_details', view=getattr(chosen_backend, 'literature_details'), renderer=renderer)
    config.add_route('literature_graph', '/locus/{identifier}/literature_graph', view=getattr(chosen_backend, 'literature_graph'), renderer=renderer)
    
    #Protein views
    config.add_route('protein_domain_details', '/locus/{identifier}/protein_domain_details', view=getattr(chosen_backend, 'protein_domain_details'), renderer=renderer)
    config.add_route('binding_site_details', '/locus/{identifier}/binding_site_details', view=getattr(chosen_backend, 'binding_site_details'), renderer=renderer)

    #GO views
    config.add_route('go_references', '/locus/{identifier}/go_references', view=getattr(chosen_backend, 'go_references'), renderer=renderer)
    config.add_route('go_enrichment', '/go_enrichment', view=getattr(chosen_backend, 'go_enrichment'), renderer=renderer)

    #Phenotype views
    config.add_route('phenotype_references', '/locus/{identifier}/phenotype_references', view=getattr(chosen_backend, 'phenotype_references'), renderer=renderer)
    
    #List views
    config.add_route('bioentity_list', '/bioentity_list', view=getattr(chosen_backend, 'bioentity_list'), renderer=renderer)
    config.add_route('reference_list', '/reference_list', view=getattr(chosen_backend, 'reference_list'), renderer=renderer)


def sgdbackend(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
        
    from sgdbackend import SGDBackend
    chosen_backend = SGDBackend(config)
    
    prep_views(chosen_backend, config)
    return config.make_wsgi_app()

def perfbackend(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
        
    from perfbackend import PerfBackend
    chosen_backend = PerfBackend(config)
    
    prep_views(chosen_backend, config)
    return config.make_wsgi_app()
