from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import sys

def prep_views(chosen_backend, config):  
    
    #Reference views
    config.add_route('all_references', '/all_references', view=getattr(chosen_backend, 'all_references'), renderer=chosen_backend.get_renderer('all_references'))
    config.add_route('all_bibentries', '/all_bibentries', view=getattr(chosen_backend, 'all_bibentries'), renderer=chosen_backend.get_renderer('all_bibentries'))
    config.add_route('reference', '/reference/{identifier}/overview', view=getattr(chosen_backend, 'reference'), renderer=chosen_backend.get_renderer('reference'))
    config.add_route('reference_list', '/reference_list', view=getattr(chosen_backend, 'reference_list'), renderer=chosen_backend.get_renderer('reference_list'))
    
    #Bioent views
    config.add_route('all_bioentities', '/all_bioentities', view=getattr(chosen_backend, 'all_bioentities'), renderer=chosen_backend.get_renderer('all_bioentities'))
    config.add_route('bioentity_list', '/bioentity_list', view=getattr(chosen_backend, 'bioentity_list'), renderer=chosen_backend.get_renderer('bioentity_list'))

    #Locus views
    config.add_route('locus', '/locus/{identifier}/overview', view=getattr(chosen_backend, 'locus'), renderer=chosen_backend.get_renderer('locus'))
    config.add_route('locustabs', '/locus/{identifier}/tabs', view=getattr(chosen_backend, 'locustabs'), renderer=chosen_backend.get_renderer('locustabs'))
    
    #Biocon views
    config.add_route('all_bioconcepts', '/all_bioconcepts', view=getattr(chosen_backend, 'all_bioconcepts'), renderer=chosen_backend.get_renderer('all_bioconcepts'))
    config.add_route('bioconcept_list', '/bioconcept_list', view=getattr(chosen_backend, 'bioentity_list'), renderer=chosen_backend.get_renderer('bioentity_list')) 
    
    #Go views
    config.add_route('go', '/go/{identifier}/overview', view=getattr(chosen_backend, 'go'), renderer=chosen_backend.get_renderer('go'))
    config.add_route('go_references', '/locus/{identifier}/go_references', view=getattr(chosen_backend, 'go_references'), renderer=chosen_backend.get_renderer('go_references'))
    config.add_route('go_enrichment', '/go_enrichment', view=getattr(chosen_backend, 'go_enrichment'), renderer=chosen_backend.get_renderer('go_enrichment'))

    #Phenotype views
    config.add_route('phenotype', '/phenotype/{identifier}/overview', view=getattr(chosen_backend, 'phenotype'), renderer=chosen_backend.get_renderer('phenotype'))    
    config.add_route('phenotype_references', '/locus/{identifier}/phenotype_references', view=getattr(chosen_backend, 'phenotype_references'), renderer=chosen_backend.get_renderer('phenotype_references'))
    
    #Interaction views
    config.add_route('interaction_overview', '/locus/{identifier}/interaction_overview', view=getattr(chosen_backend, 'interaction_overview'), renderer=chosen_backend.get_renderer('interaction_overview'))
    config.add_route('interaction_details', '/locus/{identifier}/interaction_details', view=getattr(chosen_backend, 'interaction_details'), renderer=chosen_backend.get_renderer('interaction_overview'))
    config.add_route('interaction_graph', '/locus/{identifier}/interaction_graph', view=getattr(chosen_backend, 'interaction_graph'), renderer=chosen_backend.get_renderer('interaction_graph'))
    config.add_route('interaction_resources', '/locus/{identifier}/interaction_resources', view=getattr(chosen_backend, 'interaction_resources'), renderer=chosen_backend.get_renderer('interaction_resources'))
    config.add_route('interaction_references', '/locus/{identifier}/interaction_references', view=getattr(chosen_backend, 'interaction_references'), renderer=chosen_backend.get_renderer('interaction_references'))
    
    #Regulation views
    config.add_route('regulation_overview', '/locus/{identifier}/regulation_overview', view=getattr(chosen_backend, 'regulation_overview'), renderer=chosen_backend.get_renderer('regulation_overview'))
    config.add_route('regulation_details', '/locus/{identifier}/regulation_details', view=getattr(chosen_backend, 'regulation_details'), renderer=chosen_backend.get_renderer('regulation_details'))
    config.add_route('regulation_graph', '/locus/{identifier}/regulation_graph', view=getattr(chosen_backend, 'regulation_graph'), renderer=chosen_backend.get_renderer('regulation_graph'))
    config.add_route('regulation_references', '/locus/{identifier}/regulation_references', view=getattr(chosen_backend, 'regulation_references'), renderer=chosen_backend.get_renderer('regulation_graph'))
    
    #Literature views
    config.add_route('literature_overview', '/locus/{identifier}/literature_overview', view=getattr(chosen_backend, 'literature_overview'), renderer=chosen_backend.get_renderer('literature_overview'))
    config.add_route('literature_details', '/locus/{identifier}/literature_details', view=getattr(chosen_backend, 'literature_details'), renderer=chosen_backend.get_renderer('literature_details'))
    config.add_route('literature_graph', '/locus/{identifier}/literature_graph', view=getattr(chosen_backend, 'literature_graph'), renderer=chosen_backend.get_renderer('literature_graph'))
    
    #Protein views
    config.add_route('protein_domain_details', '/locus/{identifier}/protein_domain_details', view=getattr(chosen_backend, 'protein_domain_details'), renderer=chosen_backend.get_renderer('protein_domain_details'))
    config.add_route('binding_site_details', '/locus/{identifier}/binding_site_details', view=getattr(chosen_backend, 'binding_site_details'), renderer=chosen_backend.get_renderer('binding_site_details'))

    #Misc
    config.add_route('all_disambigs', '/all_disambigs', view=getattr(chosen_backend, 'all_disambigs'), renderer=chosen_backend.get_renderer('all_disambigs'))    

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
