from pyramid.config import Configurator

import config


__author__ = 'kpaskov'

def prep_views(chosen_backend, config):
    
    #Chemical views
    config.add_route('chemical', 
                     '/chemical/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('chemical', request)(
                                getattr(chosen_backend, 'chemical')(
                                        chemical_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('chemical'))
    
    #Reference views
    config.add_route('reference', 
                     '/reference/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('reference', request)(
                                getattr(chosen_backend, 'reference')(
                                        reference_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('reference'))
    
    config.add_route('reference_list', 
                     '/reference_list', 
                     view=lambda request: chosen_backend.response_wrapper('reference_list', request)(
                                getattr(chosen_backend, 'reference_list')(
                                        None if 'reference_ids' not in request.json_body else request.json_body['reference_ids'])),
                     renderer=chosen_backend.get_renderer('reference_list'))

    config.add_route('author',
                     '/author/{identifier}/overview',
                     view=lambda request: chosen_backend.response_wrapper('author', request)(
                                getattr(chosen_backend, 'author')(
                                        author_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('author'))

    config.add_route('author_references',
                     '/author/{identifier}/references',
                     view=lambda request: chosen_backend.response_wrapper('author_references', request)(
                                getattr(chosen_backend, 'author_references')(
                                        author_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('author_references'))

    config.add_route('references_this_week',
                     '/references/this_week',
                     view=lambda request: chosen_backend.response_wrapper('references_this_week', request)(
                                getattr(chosen_backend, 'references_this_week')()),
                     renderer=chosen_backend.get_renderer('references_this_week'))
    
    #Bioent views
    config.add_route('bioentity_list', 
                     '/bioentity_list', 
                     view=lambda request: chosen_backend.response_wrapper('bioentity_list', request)(
                                getattr(chosen_backend, 'bioentity_list')(
                                        None if 'bioent_ids' not in request.json_body else request.json_body['bioent_ids'])),
                     renderer=chosen_backend.get_renderer('bioentity_list'))

    #Locus views
    config.add_route('locus', 
                     '/locus/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('locus', request)(
                                getattr(chosen_backend, 'locus')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('locus'))

    config.add_route('locus_alias',
                     '/locus/{identifier}/alias',
                     view=lambda request: chosen_backend.response_wrapper('locus_alias', request)(
                                getattr(chosen_backend, 'locus_alias')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('locus_alias'))
    
    config.add_route('locustabs', 
                     '/locus/{identifier}/tabs', 
                     view=lambda request: chosen_backend.response_wrapper('locustabs', request)(
                                getattr(chosen_backend, 'locustabs')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('locustabs'))
    
    #Go views
    config.add_route('go', 
                     '/go/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('go', request)(
                                getattr(chosen_backend, 'go')(
                                        go_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('go'))
    
    config.add_route('go_ontology_graph', 
                     '/go/{identifier}/ontology_graph', 
                     view=lambda request: chosen_backend.response_wrapper('go_ontology_graph', request)(
                                getattr(chosen_backend, 'go_ontology_graph')(
                                        go_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('go_ontology_graph'))
    
    config.add_route('go_overview', 
                     '/locus/{identifier}/go_overview', 
                     view=lambda request: chosen_backend.response_wrapper('go_overview', request)(
                                getattr(chosen_backend, 'go_overview')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('go_overview'))
    
    config.add_route('go_bioent_details', 
                     '/locus/{identifier}/go_details', 
                     view=lambda request: chosen_backend.response_wrapper('go_details', request)(
                                getattr(chosen_backend, 'go_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('go_details'))
    
    config.add_route('go_biocon_details', 
                     '/go/{identifier}/locus_details', 
                     view=lambda request: chosen_backend.response_wrapper('go_details', request)(
                                getattr(chosen_backend, 'go_details')(
                                        go_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])), 
                     renderer=chosen_backend.get_renderer('go_details'))
    
    config.add_route('go_biocon_details_all', 
                     '/go/{identifier}/locus_details_all', 
                     view=lambda request: chosen_backend.response_wrapper('go_details', request)(
                                getattr(chosen_backend, 'go_details')(
                                        go_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'],
                                        with_children=True)), 
                     renderer=chosen_backend.get_renderer('go_details'))

    config.add_route('go_ref_details',
                     '/reference/{identifier}/go_details',
                     view=lambda request: chosen_backend.response_wrapper('go_details', request)(
                                getattr(chosen_backend, 'go_details')(
                                        reference_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('go_details'))
    
    config.add_route('go_enrichment', 
                     '/go_enrichment', 
                     view=lambda request: chosen_backend.response_wrapper('go_enrichment', request)(
                                getattr(chosen_backend, 'go_enrichment')(
                                       None if 'bioent_ids' not in request.json_body else request.json_body['bioent_ids'])),
                     renderer=chosen_backend.get_renderer('go_enrichment'))

    config.add_route('go_graph', '/locus/{identifier}/go_graph',
                     view=lambda request: chosen_backend.response_wrapper('go_graph', request)(
                                getattr(chosen_backend, 'go_graph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('go_graph'))

    #Phenotype views
    config.add_route('phenotype', 
                     '/phenotype/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype', request)(
                                getattr(chosen_backend, 'phenotype')(
                                        phenotype_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype'))   

    config.add_route('phenotype_ontology_graph', 
                     '/phenotype/{identifier}/ontology_graph', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_ontology_graph', request)(
                                getattr(chosen_backend, 'phenotype_ontology_graph')(
                                        phenotype_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype_ontology_graph'))
    
    config.add_route('phenotype_ontology', 
                     '/phenotype/ontology', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_ontology', request)(
                                getattr(chosen_backend, 'phenotype_ontology')()),
                     renderer=chosen_backend.get_renderer('phenotype_ontology'))
        
    config.add_route('phenotype_bioent_overview',
                     '/locus/{identifier}/phenotype_overview', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_overview', request)(
                                getattr(chosen_backend, 'phenotype_overview')(
                                        locus_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype_overview'))

    config.add_route('phenotype_biocon_overview',
                     '/phenotype/{identifier}/phenotype_overview',
                     view=lambda request: chosen_backend.response_wrapper('phenotype_overview', request)(
                                getattr(chosen_backend, 'phenotype_overview')(
                                        phenotype_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype_overview'))
    
    config.add_route('phenotype_bioent_details', 
                     '/locus/{identifier}/phenotype_details', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details', request)(
                                getattr(chosen_backend, 'phenotype_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])), 
                     renderer=chosen_backend.get_renderer('phenotype_details'))
    
    config.add_route('phenotype_biocon_details', 
                     '/phenotype/{identifier}/locus_details', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details', request)(
                                getattr(chosen_backend, 'phenotype_details')(
                                        phenotype_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])), 
                     renderer=chosen_backend.get_renderer('phenotype_details')) 
    
    config.add_route('phenotype_biocon_details_all', 
                     '/phenotype/{identifier}/locus_details_all', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details', request)(
                                getattr(chosen_backend, 'phenotype_details')(
                                        phenotype_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'],
                                        with_children=True)), 
                     renderer=chosen_backend.get_renderer('phenotype_details'))
    
    config.add_route('phenotype_chem_details', 
                     '/chemical/{identifier}/phenotype_details',
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details', request)(
                                getattr(chosen_backend, 'phenotype_details')(
                                        chemical_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])), 
                     renderer=chosen_backend.get_renderer('phenotype_details'))

    config.add_route('phenotype_ref_details',
                     '/reference/{identifier}/phenotype_details',
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details', request)(
                                getattr(chosen_backend, 'phenotype_details')(
                                        reference_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype_details'))

    config.add_route('phenotype_resources',
                     '/locus/{identifier}/phenotype_resources',
                     view=lambda request: chosen_backend.response_wrapper('phenotype_resources', request)(
                                getattr(chosen_backend, 'phenotype_resources')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype_resources'))

    config.add_route('phenotype_graph', '/locus/{identifier}/phenotype_graph',
                     view=lambda request: chosen_backend.response_wrapper('phenotype_graph', request)(
                                getattr(chosen_backend, 'phenotype_graph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('phenotype_graph'))

    #Complex
    config.add_route('complex',
                     '/complex/{identifier}/overview',
                     view=lambda request: chosen_backend.response_wrapper('complex', request)(
                                getattr(chosen_backend, 'complex')(
                                        complex_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('complex'))

    config.add_route('complex_complex_details',
                     '/complex/{identifier}/locus_details',
                     view=lambda request: chosen_backend.response_wrapper('complex_details', request)(
                                getattr(chosen_backend, 'complex_details')(
                                        complex_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('complex_details'))

    config.add_route('complex_bioent_details',
                     '/locus/{identifier}/complex_details',
                     view=lambda request: chosen_backend.response_wrapper('complex_details', request)(
                                getattr(chosen_backend, 'complex_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('complex_details'))

    config.add_route('complex_graph',
                     '/complex/{identifier}/graph',
                     view=lambda request: chosen_backend.response_wrapper('complex_graph', request)(
                                getattr(chosen_backend, 'complex_graph')(
                                        complex_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('complex_graph'))
    
    #Interaction views
    config.add_route('interaction_overview', 
                     '/locus/{identifier}/interaction_overview', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_overview', request)(
                                getattr(chosen_backend, 'interaction_overview')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('interaction_overview'))
    
    config.add_route('interaction_bioent_details',
                     '/locus/{identifier}/interaction_details', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_details', request)(
                                getattr(chosen_backend, 'interaction_details')(
                                        locus_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('interaction_overview'))

    config.add_route('interaction_ref_details',
                     '/reference/{identifier}/interaction_details',
                     view=lambda request: chosen_backend.response_wrapper('interaction_details', request)(
                                getattr(chosen_backend, 'interaction_details')(
                                        reference_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('interaction_details'))
    
    config.add_route('interaction_graph', 
                     '/locus/{identifier}/interaction_graph', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_graph', request)(
                                getattr(chosen_backend, 'interaction_graph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('interaction_graph'))
    
    config.add_route('interaction_resources', 
                     '/locus/{identifier}/interaction_resources', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_resources', request)(
                                getattr(chosen_backend, 'interaction_resources')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('interaction_resources'))
    
    #Regulation views
    config.add_route('regulation_overview', 
                     '/locus/{identifier}/regulation_overview/{filter}',
                     view=lambda request: chosen_backend.response_wrapper('regulation_overview', request)(
                                getattr(chosen_backend, 'regulation_overview')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'],
                                        filter = None if 'filter' not in request.matchdict else request.matchdict['filter'])),
                     renderer=chosen_backend.get_renderer('regulation_overview'))
    
    config.add_route('regulation_bioent_details',
                     '/locus/{identifier}/regulation_details/{filter}',
                     view=lambda request: chosen_backend.response_wrapper('regulation_details', request)(
                                getattr(chosen_backend, 'regulation_details')(
                                        locus_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'],
                                        filter = None if 'filter' not in request.matchdict else request.matchdict['filter'])),
                     renderer=chosen_backend.get_renderer('regulation_details'))

    config.add_route('regulation_ref_details',
                     '/reference/{identifier}/regulation_details',
                     view=lambda request: chosen_backend.response_wrapper('regulation_details', request)(
                                getattr(chosen_backend, 'regulation_details')(
                                        reference_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('regulation_details'))
    
    config.add_route('regulation_target_enrichment', 
                     '/locus/{identifier}/regulation_target_enrichment', 
                     view=lambda request: chosen_backend.response_wrapper('regulation_target_enrichment', request)(
                                getattr(chosen_backend, 'regulation_target_enrichment')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('regulation_target_enrichment'))
    
    config.add_route('regulation_graph', 
                     '/locus/{identifier}/regulation_graph/{filter}',
                     view=lambda request: chosen_backend.response_wrapper('regulation_graph', request)(
                                getattr(chosen_backend, 'regulation_graph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'],
                                        filter = None if 'filter' not in request.matchdict else request.matchdict['filter'])),
                     renderer=chosen_backend.get_renderer('regulation_graph'))

    config.add_route('regulation_paragraph',
                     '/locus/{identifier}/regulation_paragraph',
                     view=lambda request: chosen_backend.response_wrapper('regulation_paragraph', request)(
                                getattr(chosen_backend, 'regulation_paragraph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('regulation_paragraph'))
    
    #Literature views
    config.add_route('literature_overview', 
                     '/locus/{identifier}/literature_overview', 
                     view=lambda request: chosen_backend.response_wrapper('literature_overview', request)(
                                getattr(chosen_backend, 'literature_overview')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('literature_overview'))
    
    config.add_route('literature_bioent_details',
                     '/locus/{identifier}/literature_details', 
                     view=lambda request: chosen_backend.response_wrapper('literature_details', request)(
                                getattr(chosen_backend, 'literature_details')(
                                        locus_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('literature_details'))

    config.add_route('literature_ref_details',
                     '/reference/{identifier}/literature_details',
                     view=lambda request: chosen_backend.response_wrapper('literature_details', request)(
                                getattr(chosen_backend, 'literature_details')(
                                        reference_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('literature_details'))

    config.add_route('literature_topic_details',
                     '/topic/{topic}/literature_details',
                     view=lambda request: chosen_backend.response_wrapper('literature_details', request)(
                                getattr(chosen_backend, 'literature_details')(
                                    topic=None if 'topic' not in request.matchdict else request.matchdict['topic'].replace('_', ' '))),
                     renderer=chosen_backend.get_renderer('literature_details'))
    
    config.add_route('literature_graph', '/locus/{identifier}/literature_graph', 
                     view=lambda request: chosen_backend.response_wrapper('literature_graph', request)(
                                getattr(chosen_backend, 'literature_graph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('literature_graph'))
    
    #Protein views
    config.add_route('protein_overview',
                     '/locus/{identifier}/protein_overview',
                     view=lambda request: chosen_backend.response_wrapper('protein_overview', request)(
                                getattr(chosen_backend, 'protein_overview')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_overview'))

    config.add_route('sequence_overview',
                     '/locus/{identifier}/sequence_overview',
                     view=lambda request: chosen_backend.response_wrapper('sequence_overview', request)(
                                getattr(chosen_backend, 'sequence_overview')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('sequence_overview'))

    config.add_route('protein_domain_bioent_details',
                     '/locus/{identifier}/protein_domain_details', 
                     view=lambda request: chosen_backend.response_wrapper('protein_domain_details', request)(
                                getattr(chosen_backend, 'protein_domain_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_domain_details'))

    config.add_route('protein_domain_bioitem_details',
                     '/domain/{identifier}/locus_details',
                     view=lambda request: chosen_backend.response_wrapper('protein_domain_details', request)(
                                getattr(chosen_backend, 'protein_domain_details')(
                                        domain_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_domain_details'))

    config.add_route('domain',
                     '/domain/{identifier}/overview',
                     view=lambda request: chosen_backend.response_wrapper('domain', request)(
                                getattr(chosen_backend, 'domain')(
                                        domain_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('domain'))

    config.add_route('protein_domain_graph', '/locus/{identifier}/protein_domain_graph',
                     view=lambda request: chosen_backend.response_wrapper('protein_domain_graph', request)(
                                getattr(chosen_backend, 'protein_domain_graph')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_domain_graph'))

    config.add_route('protein_resources', '/locus/{identifier}/protein_resources',
                     view=lambda request: chosen_backend.response_wrapper('protein_resources', request)(
                                getattr(chosen_backend, 'protein_resources')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_resources'))
    
    config.add_route('binding_site_bioent_details',
                     '/locus/{identifier}/binding_site_details', 
                     view=lambda request: chosen_backend.response_wrapper('binding_site_details', request)(
                                getattr(chosen_backend, 'binding_site_details')(
                                        locus_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('binding_site_details'))

    #EC Number views
    config.add_route('ecnumber',
                     '/ecnumber/{identifier}/overview',
                     view=lambda request: chosen_backend.response_wrapper('ec_number', request)(
                                getattr(chosen_backend, 'ec_number')(
                                        ec_number_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('ec_number'))

    config.add_route('ecnumber_ontology_graph',
                     '/ecnumber/{identifier}/ontology_graph',
                     view=lambda request: chosen_backend.response_wrapper('ec_number_ontology_graph', request)(
                                getattr(chosen_backend, 'ec_number_ontology_graph')(
                                        ec_number_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('ec_number_ontology_graph'))

    config.add_route('ecnumber_bioent_details',
                     '/locus/{identifier}/ecnumber_details',
                     view=lambda request: chosen_backend.response_wrapper('ec_number_details', request)(
                                getattr(chosen_backend, 'ec_number_details')(
                                        locus_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('ec_number_details'))

    config.add_route('ecnumber_biocon_details',
                     '/ecnumber/{identifier}/locus_details',
                     view=lambda request: chosen_backend.response_wrapper('ec_number_details', request)(
                                getattr(chosen_backend, 'ec_number_details')(
                                        ec_number_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('ec_number_details'))

    config.add_route('ecnumber_biocon_details_all',
                     '/ecnumber/{identifier}/locus_details_all',
                     view=lambda request: chosen_backend.response_wrapper('ec_number_details', request)(
                                getattr(chosen_backend, 'ec_number_details')(
                                        ec_number_identifier = None if 'identifier' not in request.matchdict else request.matchdict['identifier'],
                                        with_children = True)),
                     renderer=chosen_backend.get_renderer('ec_number_details'))

    #Sequence views
    config.add_route('sequence_bioent_details',
                     '/locus/{identifier}/sequence_details',
                     view=lambda request: chosen_backend.response_wrapper('sequence_details', request)(
                                getattr(chosen_backend, 'sequence_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('sequence_details'))

    config.add_route('sequence_neighbor_details',
                     '/locus/{identifier}/neighbor_sequence_details',
                     view=lambda request: chosen_backend.response_wrapper('neighbor_sequence_details', request)(
                                getattr(chosen_backend, 'neighbor_sequence_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('neighbor_sequence_details'))

    config.add_route('sequence_contig_details',
                     '/contig/{identifier}/sequence_details',
                     view=lambda request: chosen_backend.response_wrapper('sequence_details', request)(
                                getattr(chosen_backend, 'sequence_details')(
                                        contig_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('sequence_details'))

    config.add_route('protein_phosphorylation_details',
                     '/locus/{identifier}/protein_phosphorylation_details',
                     view=lambda request: chosen_backend.response_wrapper('protein_phosphorylation_details', request)(
                                getattr(chosen_backend, 'protein_phosphorylation_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_phosphorylation_details'))

    config.add_route('protein_experiment_details',
                     '/locus/{identifier}/protein_experiment_details',
                     view=lambda request: chosen_backend.response_wrapper('protein_experiment_details', request)(
                                getattr(chosen_backend, 'protein_experiment_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('protein_experiment_details'))

    config.add_route('contig',
                     '/contig/{identifier}/overview',
                     view=lambda request: chosen_backend.response_wrapper('contig', request)(
                                getattr(chosen_backend, 'contig')(
                                        contig_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier'])),
                     renderer=chosen_backend.get_renderer('contig'))


    
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

