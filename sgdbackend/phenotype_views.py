'''
Created on Mar 15, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent
from sgdbackend.utils import make_reference_list
#
#
#
#'''
#-------------------------------Views---------------------------------------
#'''
#@view_config(route_name='phenotype', renderer='json')
#def phenotype(request):
#    biocon_name = request.matchdict['biocon']
#    biocon = get_biocon(biocon_name, 'PHENOTYPE')
#    if biocon is None:
#        return Response(status_int=500, body='Biocon could not be found.')
#    
#    biocon_json = {
#                    'display_name': biocon.display_name, 
#                    'format_name': biocon.format_name,
#                    'description': biocon.description,
#                   }
#    return biocon_json
#
#@view_config(route_name='phenotype_overview_table', renderer='jsonp')
#def phenotype_overview_table(request):
#    if 'biocon' in request.GET:
#        #Need a phenotype overview table based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon_id = get_biocon_id(biocon_name, 'PHENOTYPE')
#        if biocon_id is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        phenoevidences = get_phenotype_evidence(biocon_id=biocon_id)
#        return make_overview_tables(False, phenoevidences) 
#        
#    elif 'bioent' in request.GET:
#        #Need a phenotype overview table based on a bioent
#        bioent_name = request.GET['bioent']
#        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
#        if bioent_id is None:
#            return Response(status_int=500, body='Bioent could not be found.')
#        phenoevidences = get_phenotype_evidence(bioent_id=bioent_id)
#        return make_overview_tables(True, phenoevidences) 
#    
#    elif 'reference' in request.GET:
#        #Need a phenotype overview table based on a reference
#        ref_name = request.GET['reference']
#        ref_id = get_reference_id(ref_name)
#        if ref_id is None:
#            return Response(status_int=500, body='Reference could not be found.')
#        phenoevidences = get_phenotype_evidence(reference_id=ref_id)
#        return make_overview_tables(True, phenoevidences) 
#    
#    elif 'chemical' in request.GET:
#        #Need a phenotype overview table based on a chemical
#        chem_name = request.GET['chemical']
#        chem_id = get_chemical_id(chem_name)
#        if chem_id is None:
#            return Response(status_int=500, body='Chemical could not be found.')
#        phenoevidences = get_phenotype_evidence(chemical_id=chem_id)
#        return make_overview_tables(False, phenoevidences) 
#
#    else:
#        return Response(status_int=500, body='No Bioent, Biocon, Reference, or Chemical specified.')
#
#
#@view_config(route_name='phenotype_evidence_table', renderer='jsonp')
#def phenotype_evidence_table(request):
#    if 'biocon' in request.GET:
#        #Need a phenotype overview table based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon_id = get_biocon_id(biocon_name, 'PHENOTYPE')
#        if biocon_id is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        evidences = get_phenotype_evidence(biocon_id=biocon_id)
#        return make_evidence_tables(False, evidences) 
#        
#    elif 'bioent' in request.GET:
#        #Need a phenotype overview table based on a bioent
#        bioent_name = request.GET['bioent']
#        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
#        if bioent_id is None:
#            return Response(status_int=500, body='Bioent could not be found.')
#        evidences = get_phenotype_evidence(bioent_id=bioent_id)
#        return make_evidence_tables(True, evidences) 
#    
#    else:
#        return Response(status_int=500, body='No Bioent or Biocon specified.')
#    
#@view_config(route_name='phenotype_ontology_graph', renderer="jsonp")
#def phenotype_ontology_graph(request):
#    if 'biocon' in request.GET:
#        #Need a phenotype ontology graph based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon = get_biocon(biocon_name, 'PHENOTYPE')
#        if biocon is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        return create_phenotype_ontology_graph(biocon=biocon)
#
#    else:
#        return Response(status_int=500, body='No Biocon specified.')
#
#@view_config(route_name='phenotype_graph', renderer="jsonp")
#def phenotype_graph(request):
#    if 'biocon' in request.GET:
#        #Need a GO graph based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon = get_biocon(biocon_name, 'PHENOTYPE')
#        if biocon is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        
#        evidence_filter = lambda x: True
#        l1_filter = lambda x, y: True
#        l2_filter = lambda x, y: x.biocon_type == 'PHENOTYPE' and len(y) > 1
#        return create_graph(['BIOENTITY'], ['BIOCONCEPT'], evidence_filter, l1_filter, l2_filter, seed_biocons=[biocon]) 
#
#  
#    elif 'bioent' in request.GET:
#        #Need a GO graph based on a bioent
#        bioent_name = request.GET['bioent']
#        bioent = get_bioent(bioent_name, 'LOCUS')
#        if bioent is None:
#            return Response(status_int=500, body='Bioent could not be found.')
#
#        evidence_filter = lambda x: True
#        l1_filter = lambda x, y: x.biocon_type == 'PHENOTYPE' and x.phenotype_type == 'cellular'
#        l2_filter = lambda x, y: len(y) > 5
#        return create_graph(['BIOCONCEPT'], ['BIOENTITY'], evidence_filter, l1_filter, l2_filter, seed_bioents=[bioent]) 
#
#    else:
#        return Response(status_int=500, body='No Bioent or Biocon specified.')

@view_config(route_name='phenotype_references', renderer="jsonp")
def phenotype_references(request):
    #Need go references based on a bioent
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return make_reference_list(['PHENO_EVIDENCE'], bioent['id'])
#
#'''
#-------------------------------Overview Table---------------------------------------
#'''
#
#def make_overview_tables(divided, phenoevidences):
#    tables = {}
#            
#    if divided:
#        divided_evidences = divide_phenoevidences(phenoevidences)
#        
#        tables['cellular_pheno'] = make_overview_table(divided_evidences['cellular'])
#        tables['chemical_pheno'] = make_chemical_overview_table(divided_evidences['chemical'])
#        tables['pp_rna_pheno'] = make_pp_rna_overview_table(divided_evidences['pp_rna'])
#    else:
#        tables['aaData'] = make_overview_table(phenoevidences)
#    return tables    
#
#def make_overview_table(phenoevidences):
#    evidence_map = dict([(evidence.id, (evidence.bioentity, evidence.bioconcept)) for evidence in phenoevidences])
#    return create_grouped_evidence_table(phenoevidences, evidence_map, make_overview_row) 
#
#def make_chemical_overview_table(phenoevidences):
#    evidence_map = dict([(evidence.id, (', '.join([chem.name_with_link for chem in evidence.chemicals]), evidence.bioentity, evidence.bioconcept)) for evidence in phenoevidences])
#    return create_grouped_evidence_table(phenoevidences, evidence_map, make_grouped_overview_row) 
#
#def make_pp_rna_overview_table(phenoevidences):
#    evidence_map = dict([(evidence.id, (evidence.reporter, evidence.bioentity, evidence.bioconcept)) for evidence in phenoevidences])
#    return create_grouped_evidence_table(phenoevidences, evidence_map, make_grouped_overview_row) 
#
#def make_overview_row(evs_for_group, group_term):
#    bioent = group_term[0]
#    biocon = group_term[1]
#    return [biocon.observable, bioent.name_with_link, biocon.qualifier, biocon.mutant_type]
#
#def make_grouped_overview_row(evs_for_group, group_term):
#    bioent = group_term[1]
#    biocon = group_term[2]
#    return [biocon.observable, bioent.name_with_link, group_term[0], biocon.qualifier, biocon.mutant_type]
#    
#'''
#-------------------------------Evidence Table---------------------------------------
#'''
#    
#def make_evidence_tables(divided, phenoevidences):
#    tables = {}
#
#    if divided:
#        divided_evidences = divide_phenoevidences(phenoevidences)
#
#        tables['cellular_pheno'] = create_simple_table(divided_evidences['cellular'], make_evidence_row)
#        tables['chemical_pheno'] = create_simple_table(divided_evidences['chemical'], make_evidence_row)
#        tables['pp_rna_pheno'] = create_simple_table(divided_evidences['pp_rna'], make_evidence_row)
#        
#    else:
#        tables['aaData'] = create_simple_table(phenoevidences, make_evidence_row)
#        
#    tables['reference'] = make_reference_list(phenoevidences)
#        
#    return tables    
#
#def make_evidence_row(phenoevidence): 
#    bioent = phenoevidence.bioentity
#    biocon = phenoevidence.bioconcept
#    reference = ''
#    if phenoevidence.reference is not None:
#        reference = phenoevidence.reference.name_with_link
#     
#    allele_entry = ''   
#    if phenoevidence.allele:
#        allele_entry = phenoevidence.allele.name
#                
#    chemicals = []
#    for chemical in phenoevidence.ev_chemicals:
#        if chemical.chemical_amt is None:
#            chemicals.append(chemical.chemical.name_with_link)
#        else:
#            chemicals.append(chemical.chemical.name_with_link + ': ' + chemical.chemical_amt)
#    if len(chemicals) > 0:
#        chemical_info = ', '.join(chemicals)
#    else:
#        chemical_info = None
#
#     
#    return [None, biocon.observable, bioent.name_with_link, 
#            biocon.qualifier, biocon.mutant_type, phenoevidence.experiment.name_with_link, allele_entry,
#            phenoevidence.reporter, chemical_info, phenoevidence.experiment_details, phenoevidence.conditions, phenoevidence.details, 
#            phenoevidence.strain.name_with_link, phenoevidence.source, reference]
#    
#'''
#------------------------------Phenotype Ontology Graph-----------------------------
#'''
#go_ontology_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
#                         {'name':'link', 'type':'string'}, 
#                         {'name':'bio_type', 'type':'string'},
#                         {'name':'sub_type', 'type':'string'},
#                         {'name':'child', 'type':'boolean'},
#                         {'name':'direct_gene_count', 'type':'integer'}],
#                'edges': [{'name': "directed", 'type': "boolean", 'defValue': True}]}
#
#def create_phenotype_ontology_node(obj, focus_node, child):
#    sub_type = 'NORMAL'
#    direct_gene_count = obj.direct_gene_count
#    if direct_gene_count == 0:
#        sub_type = 'NO_GENES'
#    if obj == focus_node:
#        sub_type = 'FOCUS'
#    name = obj.display_name.replace(' ', '\n')
#    size = int(math.ceil(math.sqrt(direct_gene_count)))
#    return {'id':'BIOCONCEPT' + str(obj.id), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type, 
#            'child':child, 'direct_gene_count':size}
#
#def create_phenotype_ontology_edge(biocon_biocon):
#    return { 'id': 'BIOCON_BIOCON' + str(biocon_biocon.id), 'source': 'BIOCONCEPT' + str(biocon_biocon.parent_id), 'target': 'BIOCONCEPT' + str(biocon_biocon.child_id)}  
#
#def create_phenotype_ontology_graph(biocon):
#    biocon_family = get_biocon_family(biocon)
#    child_ids = biocon_family['child_ids']
#    nodes = [create_phenotype_ontology_node(b, biocon, b.id in child_ids) for b in biocon_family['family']]
#    edges = [create_phenotype_ontology_edge(e) for e in get_biocon_biocons(biocon_family['all_ids'])]
#        
#    return {'dataSchema':go_ontology_schema, 'data': {'nodes': nodes, 'edges': edges}, 'has_children':len(child_ids)>0}
# 
#
#'''
#-------------------------------Utils---------------------------------------
#'''  
#def divide_phenoevidences(phenoevidences):
#    chemical_phenoevidences = [phenoevidence for phenoevidence in phenoevidences if phenoevidence.bioconcept.phenotype_type == 'chemical']
#    pp_rna_phenoevidences = [phenoevidence for phenoevidence in phenoevidences if phenoevidence.bioconcept.phenotype_type == 'pp_rna']
#    cellular_phenoevidences = [phenoevidence for phenoevidence in phenoevidences if phenoevidence.bioconcept.phenotype_type == 'cellular']
#    return {'cellular':cellular_phenoevidences, 'chemical':chemical_phenoevidences, 'pp_rna':pp_rna_phenoevidences}
#
#def divide_biofacts(biofacts):
#    chemical_biofacts = [biofact for biofact in biofacts if phenotype.phenotype_type == 'chemical']
#    pp_rna_biofacts = [biofact for biofact in biofacts if phenotype.phenotype_type == 'pp_rna']
#    cellular_biofacts = [biofact for biofact in biofacts if phenotype.phenotype_type == 'cellular']
#
#    return {'cellular':cellular_biofacts, 'chemical':chemical_biofacts, 'pp_rna':pp_rna_biofacts}
#        
