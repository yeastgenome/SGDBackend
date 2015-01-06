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

    config.add_route('experiment', '/experiment/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('experiment', request)(getattr(chosen_backend, 'experiment')(experiment_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('experiment'),
                    route_name='experiment')
    
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

    #Expression views
    config.add_route('expression_details', '/locus/{identifier}/expression_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('expression_details', request)(getattr(chosen_backend, 'expression_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('expression_details'),
                    route_name='expression_details')

    config.add_route('expression_graph', '/locus/{identifier}/expression_graph')
    config.add_view(lambda request: chosen_backend.response_wrapper('expression_graph', request)(getattr(chosen_backend, 'expression_graph')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('expression_graph'),
                    route_name='expression_graph')

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

    config.add_route('domain_enrichment', '/domain/{identifier}/enrichment')
    config.add_view(lambda request: chosen_backend.response_wrapper('domain_enrichment', request)(getattr(chosen_backend, 'domain_enrichment')(domain_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('domain_enrichment'),
                    route_name='domain_enrichment')

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

    config.add_route('alignment_details', '/locus/{identifier}/alignment_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('alignment_details', request)(getattr(chosen_backend, 'alignment_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('alignment_details'),
                    route_name='alignment_details')

    config.add_route('protein_phosphorylation_details', '/locus/{identifier}/protein_phosphorylation_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_phosphorylation_details', request)(getattr(chosen_backend, 'protein_phosphorylation_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_phosphorylation_details'),
                    route_name='protein_phosphorylation_details')

    config.add_route('protein_experiment_details', '/locus/{identifier}/protein_experiment_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('protein_experiment_details', request)(getattr(chosen_backend, 'protein_experiment_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('protein_experiment_details'),
                    route_name='protein_experiment_details')

    config.add_route('history_details', '/locus/{identifier}/history_details')
    config.add_view(lambda request: chosen_backend.response_wrapper('history_details', request)(getattr(chosen_backend, 'history_details')(locus_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('history_details'),
                    route_name='history_details')

    config.add_route('contig', '/contig/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('contig', request)(getattr(chosen_backend, 'contig')(contig_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('contig'),
                    route_name='contig')

    config.add_route('dataset', '/dataset/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('dataset', request)(getattr(chosen_backend, 'dataset')(dataset_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('dataset'),
                    route_name='dataset')

    config.add_route('tag', '/tag/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('tag', request)(getattr(chosen_backend, 'tag')(tag_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('tag'),
                    route_name='tag')

    config.add_route('tag_list', '/tag')
    config.add_view(lambda request: chosen_backend.response_wrapper('tag_list', request)(getattr(chosen_backend, 'tag_list')()),
                    renderer=chosen_backend.get_renderer('tag_list'),
                    route_name='tag_list')

    config.add_route('locus_list', '/locus/{list_type}')
    config.add_view(lambda request: chosen_backend.response_wrapper('locus_list', request)(getattr(chosen_backend, 'locus_list')(list_type=request.matchdict['list_type'])),
                    renderer=chosen_backend.get_renderer('locus_list'),
                    route_name='locus_list')

    config.add_route('snapshot', '/snapshot')
    config.add_view(lambda request: chosen_backend.response_wrapper('snapshot', request)(getattr(chosen_backend, 'snapshot')()),
                    renderer=chosen_backend.get_renderer('snapshot'),
                    route_name='snapshot')

    config.add_route('reserved_name', '/reserved_name/{identifier}/overview')
    config.add_view(lambda request: chosen_backend.response_wrapper('reserved_name', request)(getattr(chosen_backend, 'reserved_name')(reserved_name_identifier=request.matchdict['identifier'])),
                    renderer=chosen_backend.get_renderer('reserved_name'),
                    route_name='reserved_name')

    
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

