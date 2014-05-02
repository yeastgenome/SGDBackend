from pyramid.config import Configurator

import config


__author__ = 'kpaskov'

def prep_views(chosen_backend, config):
    
    #Chemical views
    config.add_route('chemical', '/chemical/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('chemical', request)(getattr(chosen_backend, 'chemical')(chemical_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('chemical'),
                    route_name='chemical')

    config.add_route('strain', '/strain/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('strain', request)(getattr(chosen_backend, 'strain')(strain_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('strain'),
                    route_name='strain')
    
    #Reference views
    config.add_route('reference', '/reference/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('reference', request)(getattr(chosen_backend, 'reference')(reference_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('reference'),
                    route_name='reference')

    config.add_route('reference_list', '/reference_list')
    config.add_view(lambda request: chosen_backend.response_wrapper('reference_list', request)(getattr(chosen_backend, 'reference_list')(None if 'reference_ids' not in request.json_body else request.json_body['reference_ids'])),
                    renderer=chosen_backend.get_renderer('reference_list'),
                    route_name='reference_list')
    
    config.add_route('author', '/author/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('author', request)(getattr(chosen_backend, 'author')(author_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('author'),
                    route_name='author')

    config.add_route('references_this_week', '/references/this_week')
    config.add_view(lambda request: chosen_backend.response_wrapper('references_this_week', request)(getattr(chosen_backend, 'references_this_week')()),
                    renderer=chosen_backend.get_renderer('references_this_week'),
                    route_name='references_this_week')
    
    #Bioent views
    config.add_route('bioentity_list', '/bioentity_list')
    config.add_view(lambda request: chosen_backend.response_wrapper('bioentity_list', request)(getattr(chosen_backend, 'bioentity_list')(None if 'bioent_ids' not in request.json_body else request.json_body['bioent_ids'])),
                    renderer=chosen_backend.get_renderer('bioentity_list'),
                    route_name='bioentity_list')

    config.add_route('locus', '/locus/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('locus', request)(getattr(chosen_backend, 'locus')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('locus'),
                    route_name='locus')

    config.add_route('locustabs', '/locus/{identifier}/tabs')
    config.add_view(lambda request: chosen_backend.response_wrapper('locustabs', request)(getattr(chosen_backend, 'locustabs')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('locustabs'),
                    route_name='locustabs')
    
    #Go views
    config.add_route('go', '/go/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('go', request)(getattr(chosen_backend, 'go')(go_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('go'),
                    route_name='go')
    
    config.add_route('go_bioent_details', '/locus/{identifier}/go_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_details', request)(getattr(chosen_backend, 'go_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('go_details'),
                    route_name='go_bioent_details')

    config.add_route('go_biocon_details', '/go/{identifier}/locus_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_details', request)(getattr(chosen_backend, 'go_details')(go_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('go_details'),
                    route_name='go_biocon_details')

    config.add_route('go_biocon_details_all', '/go/{identifier}/locus_details_all')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_details', request)(getattr(chosen_backend, 'go_details')(go_identifier=request.matchdict['identifier'], with_children=True)),
                    renderer=chosen_backend.get_renderer('go_details'),
                    route_name='go_biocon_details_all')
    
    config.add_route('go_ref_details', '/reference/{identifier}/go_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_details', request)(getattr(chosen_backend, 'go_details')(reference_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('go_details'),
                    route_name='go_ref_details')

    config.add_route('go_enrichment', '/go_enrichment')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_enrichment', request)(getattr(chosen_backend, 'go_enrichment')(None if 'bioent_ids' not in request.json_body else request.json_body['bioent_ids'])),
                    renderer=chosen_backend.get_renderer('go_enrichment'),
                    route_name='go_enrichment')
    
    config.add_route('go_graph', '/locus/{identifier}/go_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_graph', request)(getattr(chosen_backend, 'go_graph')(request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('go_graph'),
                    route_name='go_graph')

    config.add_route('go_ontology_graph', '/go/{identifier}/ontology_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('go_ontology_graph', request)(getattr(chosen_backend, 'go_ontology_graph')(request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('go_ontology_graph'),
                    route_name='go_ontology_graph')

    #Phenotype views
    config.add_route('phenotype', '/phenotype/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype', request)(getattr(chosen_backend, 'phenotype')(phenotype_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype'),
                    route_name='phenotype')

    config.add_route('observable', '/observable/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('observable', request)(getattr(chosen_backend, 'observable')(observable_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('observable'),
                    route_name='observable')

    config.add_route('phenotype_bioent_details', '/locus/{identifier}/phenotype_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_details', request)(getattr(chosen_backend, 'phenotype_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_details'),
                    route_name='phenotype_bioent_details')

    config.add_route('phenotype_biocon_details', '/phenotype/{identifier}/locus_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_details', request)(getattr(chosen_backend, 'phenotype_details')(phenotype_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_details'),
                    route_name='phenotype_biocon_details')

    config.add_route('phenotype_obs_details', '/observable/{identifier}/locus_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_details', request)(getattr(chosen_backend, 'phenotype_details')(observable_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_details'),
                    route_name='phenotype_obs_details')

    config.add_route('phenotype_obs_details_all', '/observable/{identifier}/locus_details_all')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_details', request)(getattr(chosen_backend, 'phenotype_details')(observable_identifier=request.matchdict['identifier'], with_children=True)),
                    renderer=chosen_backend.get_renderer('phenotype_details'),
                    route_name='phenotype_obs_details_all')
    
    config.add_route('phenotype_chem_details', '/chemical/{identifier}/phenotype_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_details', request)(getattr(chosen_backend, 'phenotype_details')(chemical_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_details'),
                    route_name='phenotype_chem_details')
    
    config.add_route('phenotype_ref_details', '/reference/{identifier}/phenotype_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_details', request)(getattr(chosen_backend, 'phenotype_details')(reference_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_details'),
                    route_name='phenotype_ref_details')

    config.add_route('phenotype_resources', '/locus/{identifier}/phenotype_resources')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_resources', request)(getattr(chosen_backend, 'phenotype_resources')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_resources'),
                    route_name='phenotype_resources')

    config.add_route('phenotype_graph', '/locus/{identifier}/phenotype_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_graph', request)(getattr(chosen_backend, 'phenotype_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_graph'),
                    route_name='phenotype_graph')

    config.add_route('phenotype_ontology_graph', '/observable/{identifier}/ontology_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('phenotype_ontology_graph', request)(getattr(chosen_backend, 'phenotype_ontology_graph')(request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('phenotype_ontology_graph'),
                    route_name='phenotype_ontology_graph')

    config.add_route('locus_graph', '/locus/{identifier}/locus_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('locus_graph', request)(getattr(chosen_backend, 'locus_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('locus_graph'),
                    route_name='locus_graph')

    #Complex
    config.add_route('complex', '/complex/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('complex', request)(getattr(chosen_backend, 'complex')(complex_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('complex'),
                    route_name='complex')

    config.add_route('complex_complex_details', '/complex/{identifier}/locus_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('complex_details', request)(getattr(chosen_backend, 'complex_details')(complex_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('complex_details'),
                    route_name='complex_complex_details')

    config.add_route('complex_bioent_details', '/locus/{identifier}/complex_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('complex_details', request)(getattr(chosen_backend, 'complex_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('complex_details'),
                    route_name='complex_bioent_details')

    config.add_route('complex_graph', '/complex/{identifier}/graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('complex_graph', request)(getattr(chosen_backend, 'complex_graph')(complex_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('complex_graph'),
                    route_name='complex_graph')

    #Interaction views
    config.add_route('interaction_bioent_details', '/locus/{identifier}/interaction_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('interaction_details', request)(getattr(chosen_backend, 'interaction_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('interaction_details'),
                    route_name='interaction_bioent_details')
    
    config.add_route('interaction_ref_details', '/reference/{identifier}/interaction_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('interaction_details', request)(getattr(chosen_backend, 'interaction_details')(reference_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('interaction_details'),
                    route_name='interaction_ref_details')

    config.add_route('interaction_graph', '/locus/{identifier}/interaction_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('interaction_graph', request)(getattr(chosen_backend, 'interaction_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('interaction_graph'),
                    route_name='interaction_graph')
    
    config.add_route('interaction_resources', '/locus/{identifier}/interaction_resources')
    config.add_view(lambda request: chosen_backend.response_wrapper('interaction_resources', request)(getattr(chosen_backend, 'interaction_resources')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('interaction_resources'),
                    route_name='interaction_resources')
    
    #Regulation views
    config.add_route('regulation_bioent_details', '/locus/{identifier}/regulation_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('regulation_details', request)(getattr(chosen_backend, 'regulation_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('regulation_details'),
                    route_name='regulation_bioent_details')
    
    config.add_route('regulation_ref_details', '/reference/{identifier}/regulation_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('regulation_details', request)(getattr(chosen_backend, 'regulation_details')(reference_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('regulation_details'),
                    route_name='regulation_ref_details')

    config.add_route('regulation_target_enrichment', '/locus/{identifier}/regulation_target_enrichment')
    config.add_view(lambda request: chosen_backend.response_wrapper('regulation_target_enrichment', request)(getattr(chosen_backend, 'regulation_target_enrichment')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('regulation_target_enrichment'),
                    route_name='regulation_target_enrichment')
    
    config.add_route('regulation_graph', '/locus/{identifier}/regulation_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('regulation_graph', request)(getattr(chosen_backend, 'regulation_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('regulation_graph'),
                    route_name='regulation_graph')

    #Literature views
    config.add_route('literature_bioent_details', '/locus/{identifier}/literature_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('literature_details', request)(getattr(chosen_backend, 'literature_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('literature_details'),
                    route_name='literature_bioent_details')
    
    config.add_route('literature_ref_details', '/reference/{identifier}/literature_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('literature_details', request)(getattr(chosen_backend, 'literature_details')(reference_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('literature_details'),
                    route_name='literature_ref_details')

    config.add_route('literature_topic_details', '/topic/{topic}/literature_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('literature_details', request)(getattr(chosen_backend, 'literature_details')(topic=request.matchdict['topic'].replace('_', ' '))),
                    renderer=chosen_backend.get_renderer('literature_details'),
                    route_name='literature_topic_details')

    config.add_route('literature_graph', '/locus/{identifier}/literature_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('literature_graph', request)(getattr(chosen_backend, 'literature_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('literature_graph'),
                    route_name='literature_graph')
    
    #Protein views
    config.add_route('protein_domain_bioent_details', '/locus/{identifier}/protein_domain_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_domain_details', request)(getattr(chosen_backend, 'protein_domain_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_domain_details'),
                    route_name='protein_domain_bioent_details')

    config.add_route('protein_domain_bioitem_details', '/domain/{identifier}/locus_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_domain_details', request)(getattr(chosen_backend, 'protein_domain_details')(domain_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_domain_details'),
                    route_name='protein_domain_bioitem_details')

    config.add_route('domain', '/domain/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('domain', request)(getattr(chosen_backend, 'domain')(domain_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('domain'),
                    route_name='domain')

    config.add_route('protein_domain_graph', '/locus/{identifier}/protein_domain_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_domain_graph', request)(getattr(chosen_backend, 'protein_domain_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_domain_graph'),
                    route_name='protein_domain_graph')

    config.add_route('protein_resources', '/locus/{identifier}/protein_resources')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_resources', request)(getattr(chosen_backend, 'protein_resources')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_resources'),
                    route_name='protein_resources')

    config.add_route('binding_site_bioent_details', '/locus/{identifier}/binding_site_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('binding_site_details', request)(getattr(chosen_backend, 'binding_site_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('binding_site_details'),
                    route_name='binding_site_bioent_details')

    #EC Number views
    config.add_route('ecnumber', '/ecnumber/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('ec_number', request)(getattr(chosen_backend, 'ec_number')(ec_number_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('ec_number'),
                    route_name='ecnumber')

    config.add_route('ecnumber_bioent_details', '/locus/{identifier}/ecnumber_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('ec_number_details', request)(getattr(chosen_backend, 'ec_number_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('ec_number_details'),
                    route_name='ecnumber_bioent_details')

    config.add_route('ecnumber_biocon_details', '/ecnumber/{identifier}/locus_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('ec_number_details', request)(getattr(chosen_backend, 'ec_number_details')(ec_number_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('ec_number_details'),
                    route_name='ecnumber_biocon_details')

    #Sequence views
    config.add_route('sequence_bioent_details', '/locus/{identifier}/sequence_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('sequence_details', request)(getattr(chosen_backend, 'sequence_details')(locus_identifier= request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('sequence_details'),
                    route_name='sequence_bioent_details')

    config.add_route('sequence_contig_details', '/contig/{identifier}/sequence_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('sequence_details', request)(getattr(chosen_backend, 'sequence_details')(contig_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('sequence_details'),
                    route_name='sequence_contig_details')

    config.add_route('sequence_neighbor_details', '/locus/{identifier}/neighbor_sequence_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('neighbor_sequence_details', request)(getattr(chosen_backend, 'neighbor_sequence_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('neighbor_sequence_details'),
                    route_name='sequence_neighbor_details')

    config.add_route('protein_phosphorylation_details', '/locus/{identifier}/protein_phosphorylation_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_phosphorylation_details', request)(getattr(chosen_backend, 'protein_phosphorylation_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_phosphorylation_details'),
                    route_name='protein_phosphorylation_details')

    config.add_route('protein_experiment_details', '/locus/{identifier}/protein_experiment_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_experiment_details', request)(getattr(chosen_backend, 'protein_experiment_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_experiment_details'),
                    route_name='protein_experiment_details')

    config.add_route('contig', '/contig/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('contig', request)(getattr(chosen_backend, 'contig')(contig_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('contig'),
                    route_name='contig')

    config.add_route('bioentity_details', '/locus/{identifier}/bioentity_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('bioentity_details', request)(getattr(chosen_backend, 'bioentity_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('bioentity_details'),
                    route_name='bioentity_details')
    
def prepare_backend(backend_type):
    configurator = Configurator()
    configurator.add_static_view('static', 'static', cache_max_age=3600)

    chosen_backend = None
    if backend_type == 'nex':
        from nex import SGDBackend
        chosen_backend = SGDBackend(config.DBTYPE, config.NEX_DBHOST, config.DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.sgdbackend_log_directory)
    elif backend_type == 'perf':
        from perf import PerfBackend
        chosen_backend = PerfBackend(config.DBTYPE, config.PERF_DBHOST, config.DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, config.perfbackend_log_directory)
        
    prep_views(chosen_backend, configurator)
    return configurator

