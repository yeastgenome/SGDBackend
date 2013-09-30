'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment.query_yeastmine import query_go_processes
from pyramid.response import Response
from pyramid.view import view_config
from sgdbackend.cache import get_cached_bioent, get_cached_biocon
from sgdbackend.utils import make_reference_list


#
#'''
#-------------------------------Views---------------------------------------
#'''
#@view_config(route_name='go', renderer='json')
#def go(request):
#    identifier = request.matchdict['identifier']
#    biocon = get_cached_biocon(identifier, 'GO')
#    if biocon is None:
#        return Response(status_int=500, body='Bioent could not be found.')
#    return biocon
#
#@view_config(route_name='go_overview', renderer='jsonp')
#def go_overview(request):
#    if 'type' in request.matchdict:
#        entity_type = request.matchdict['type']
#        identifier = request.matchdict['identifier']
#        bioent = get_cached_bioent(identifier, entity_type)
#        if bioent is None:
#            return Response(status_int=500, body= entity_type + ' ' + str(identifier) + ' could not be found.')
#        
#        genetic = get_interactions('GENETIC_INTERACTION', bioent['id'])
#        physical = get_interactions('PHYSICAL_INTERACTION', bioent['id'])
#        return make_overview(genetic, physical, bioent) 
#    else:
#        
#    

#
#@view_config(route_name='go_evidence_table', renderer='jsonp')
#def go_evidence_table(request):
#    if 'biocon' in request.GET:
#        #Need a GO overview table based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon_id = get_biocon_id(biocon_name, 'GO')
#        if biocon_id is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        evidences = get_go_evidence(biocon_id=biocon_id)
#        return make_evidence_tables(False, evidences) 
#        
#    elif 'bioent' in request.GET:
#        #Need a GO overview table based on a bioent
#        bioent_name = request.GET['bioent']
#        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
#        if bioent_id is None:
#            return Response(status_int=500, body='Bioent could not be found.')
#        evidences = get_go_evidence(bioent_id=bioent_id)
#        return make_evidence_tables(True, evidences) 
#    
#    else:
#        return Response(status_int=500, body='No Bioent or Biocon specified.')
#    
#@view_config(route_name='go_graph', renderer="jsonp")
#def go_graph(request):
#    if 'biocon' in request.GET:
#        #Need a GO graph based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon = get_biocon(biocon_name, 'GO')
#        if biocon is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        
#        evidence_filter = lambda x: x.evidence_type != 'GO_EVIDENCE' or x.annotation_type != 'computational'
#        l1_filter = lambda x, y: True
#        l2_filter = lambda x, y: x.biocon_type == 'GO' and len(y) > 1
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
#        evidence_filter = lambda x: x.evidence_type != 'GO_EVIDENCE' or x.annotation_type != 'computational'
#        l1_filter = lambda x, y: x.biocon_type == 'GO'
#        l2_filter = lambda x, y: len(y) > 1
#        return create_graph(['BIOCONCEPT'], ['BIOENTITY'], evidence_filter, l1_filter, l2_filter, seed_bioents=[bioent]) 
#
#    else:
#        return Response(status_int=500, body='No Bioent or Biocon specified.')
#    
#@view_config(route_name='go_ontology_graph', renderer="jsonp")
#def go_ontology_graph(request):
#    if 'biocon' in request.GET:
#        #Need a GO ontology graph based on a biocon
#        biocon_name = request.GET['biocon']
#        biocon = get_biocon(biocon_name, 'GO')
#        if biocon is None:
#            return Response(status_int=500, body='Biocon could not be found.')
#        return create_go_ontology_graph(biocon=biocon)
#
#    else:
#        return Response(status_int=500, body='No Biocon specified.')


@view_config(route_name='go_references', renderer="jsonp")
def go_references(request):
    #Need go references based on a bioent
    entity_type = request.matchdict['type']
    identifier = request.matchdict['identifier']
    bioent = get_cached_bioent(identifier, entity_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
    return make_reference_list(['GO'], bioent['id'], only_primary=True)

@view_config(route_name='go_enrichment', renderer="jsonp")
def go_enrichment(request):
    bioent_format_names = request.GET['bioent_format_names'][1:-1].split(',')
    bioent_format_names = [x[1:-1] for x in bioent_format_names]
    enrichment_results = query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        goterm = get_cached_biocon(str(int(enrichment_result[0][3:])), 'GO')
        json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
    return json_format

#
#'''
#-------------------------------Overview Table---------------------------------------
#'''
#
#def make_overview_tables(divided, goevidences, include_comp=True):
#    tables = {}
#    
#    if not include_comp:
#        tables['computational'] = len(set([(evidence.bioent_id, evidence.biocon_id) for evidence in goevidences if evidence.annotation_type == 'computational']))
#        goevidences = [evidence for evidence in goevidences if evidence.annotation_type != 'computational']
#        
#    if divided:
#        divided_goevidences = divide_goevidences(goevidences)
#        
#        tables['go_p'] = make_single_overview_table(divided_goevidences['process'])
#        tables['go_f'] = make_single_overview_table(divided_goevidences['function'])
#        tables['go_c'] = make_single_overview_table(divided_goevidences['component'])
#    else:
#        tables['aaData'] = make_single_overview_table(goevidences)
#    return tables    
#
#def make_single_overview_table(goevidences):
#    evidence_map = dict([(evidence.id, (evidence.bioentity, evidence.bioconcept)) for evidence in goevidences])
#    return create_grouped_evidence_table(goevidences, evidence_map, make_overview_row)
#
#def make_overview_row(evs_for_group, group_term):
#    ev_codes = ''
#    if evs_for_group is not None:
#        evidence_codes = set([ev.go_evidence for ev in evs_for_group])
#        ev_codes = ', '.join(sorted(evidence_codes))
#        
#    bioent = group_term[0]
#    biocon = group_term[1]
#    return [biocon.name_with_link, bioent.name_with_link, bioent.description, ev_codes]
#    
#'''
#-------------------------------Evidence Table---------------------------------------
#'''
#    
#def make_evidence_tables(divided, goevidences, include_comp=True):
#    tables = {}
#
#    if not include_comp:
#        goevidences = [evidence for evidence in goevidences if evidence.annotation_type != 'computational']
#        tables['computational'] = len([evidence for evidence in goevidences if evidence.annotation_type == 'computational'])
#        
#    if divided:
#        divided_evidences = divide_goevidences(goevidences)
#        tables['go_p'] = create_simple_table(divided_evidences['process'], make_evidence_row)
#        tables['go_f'] = create_simple_table(divided_evidences['function'], make_evidence_row)
#        tables['go_c'] = create_simple_table(divided_evidences['component'], make_evidence_row)
#    else:
#        tables['aaData'] = create_simple_table(goevidences, make_evidence_row)
#        
#    tables['reference'] = make_reference_list(goevidences)
#        
#    return tables    
#
#def make_evidence_row(goevidence): 
#    bioent = goevidence.bioentity
#    biocon = goevidence.bioconcept
#    reference = ''
#    if goevidence.reference is not None:
#        reference = goevidence.reference.name_with_link
#    return [biocon.name_with_link, bioent.name_with_link, goevidence.go_evidence, goevidence.annotation_type, goevidence.qualifier, 
#            goevidence.source, reference]
#
#'''
#------------------------------GO Ontology Graph-----------------------------
#'''
#go_ontology_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
#                         {'name':'link', 'type':'string'}, 
#                         {'name':'bio_type', 'type':'string'},
#                         {'name':'sub_type', 'type':'string'},
#                         {'name':'child', 'type':'boolean'},
#                         {'name':'direct_gene_count', 'type':'integer'}],
#                'edges': [{'name': "directed", 'type': "boolean", 'defValue': True}]}
#
#def create_go_ontology_node(obj, focus_node, child):
#    sub_type = obj.go_aspect.upper()
#    direct_gene_count = obj.direct_gene_count
#    if direct_gene_count == 0:
#        sub_type = 'NO_GENES'
#    if obj == focus_node:
#        sub_type = 'FOCUS'
#    name = obj.display_name.replace(' ', '\n')
#    size = 2*int(math.ceil(math.sqrt(direct_gene_count)))
#    return {'id':'BIOCONCEPT' + str(obj.id), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type, 
#            'child':child, 'direct_gene_count':size}
#
#def create_go_ontology_edge(biocon_biocon):
#    return { 'id': 'BIOCON_BIOCON' + str(biocon_biocon.id), 'source': 'BIOCONCEPT' + str(biocon_biocon.parent_id), 'target': 'BIOCONCEPT' + str(biocon_biocon.child_id)}  
#
#    
#def create_go_ontology_graph(biocon):
#    
#    biocon_family = get_biocon_family(biocon)
#    child_ids = biocon_family['child_ids']
#    nodes = [create_go_ontology_node(b, biocon, b.id in child_ids) for b in biocon_family['family']]
#    edges = [create_go_ontology_edge(e) for e in get_biocon_biocons(biocon_family['all_ids'])]
#        
#    return {'dataSchema':go_ontology_schema, 'data': {'nodes': nodes, 'edges': edges}, 'has_children':len(child_ids)>0}
# 
#'''
#------------------------------GO Graph-----------------------------
#'''
#
#go_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
#                         {'name':'link', 'type':'string'}, 
#                         {'name':'bio_type', 'type':'string'},
#                         {'name':'sub_type', 'type':'string'},
#                         {'name':'f_include', 'type':'boolean'},
#                         {'name':'p_include', 'type':'boolean'},
#                         {'name':'c_include', 'type':'boolean'}],
#                'edges': []}
#
#def create_go_node(obj, focus_node, f_include, p_include, c_include):
#    sub_type = None
#    if obj.type == 'GO':
#        sub_type = obj.go_aspect.upper()
#    if obj == focus_node:
#        sub_type = 'FOCUS'
#    name = obj.display_name.replace(' ', '\n')
#    return {'id':get_id(obj), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type,
#            'f_include':f_include, 'p_include':p_include, 'c_include':c_include}
#
#def create_go_edge(obj, source_obj, sink_obj):
#    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj),}  
#
#aspect_to_index = {'molecular function':0, 'biological process':1, 'cellular component':2}
#def create_go_graph(bioent=None, biocon=None):
#
#    usable_bios = set()       
#   
#    if bioent is not None:
#        level_one = get_biofacts('GO', bioent=bioent)
#        level_one = [biofact for biofact in level_one if biofact.use_in_graph == 'Y']
#
#        biocon_ids = [biofact.biocon_id for biofact in level_one]
#        level_two = get_related_biofacts('GO', biocon_ids=biocon_ids)
#        
#        usable_bios.add(bioent)
#        usable_bios.update([biofact.bioconcept for biofact in level_one])
#    elif biocon is not None:
#        level_one = get_biofacts('GO', biocon=biocon)
#        level_one = [biofact for biofact in level_one if biofact.use_in_graph == 'Y']
#
#        bioent_ids = [biofact.bioent_id for biofact in level_one]
#        level_two = get_related_biofacts('GO', bioent_ids=bioent_ids)
#        
#        usable_bios.add(biocon)
#        usable_bios.update([biofact.bioentity for biofact in level_one])
#    
#    
#    bioent_to_edge_counts = {}
#    for biofact in level_two:
#        ent = biofact.bioentity
#        con = biofact.bioconcept
#        
#        index = aspect_to_index[con.go_aspect]
#            
#        if ent in bioent_to_edge_counts:
#            bioent_to_edge_counts[ent][index] = bioent_to_edge_counts[ent][index] + 1
#        else:
#            bioent_to_edge_counts[ent] = [0, 0, 0]
#            bioent_to_edge_counts[ent][index] = 1
#       
#    more_usable_bios = [bio for bio in bioent_to_edge_counts.keys() if sum(bioent_to_edge_counts[bio]) > 1]
#    if len(more_usable_bios) < 150:
#        usable_bios.update(more_usable_bios)
#        disable_cellular = False
#    else:
#        usable_bios.difference_update([biocon for biocon in usable_bios if biocon.type == 'BIOENTITY' or biocon.go_aspect == 'cellular component'])
#        not_cellular_component = [biofact.bioentity for biofact in level_two 
#                                  if biofact.bioconcept.go_aspect != 'cellular component' 
#                                  and (bioent_to_edge_counts[biofact.bioentity][0] >1 
#                                       or bioent_to_edge_counts[biofact.bioentity][1] > 1)]
#        usable_bios.update(not_cellular_component)
#        disable_cellular = True
#         
#    nodes = []  
#    for usable in usable_bios:
#        if usable.type == 'LOCUS':
#            counts = bioent_to_edge_counts[usable]
#            nodes.append(create_go_node(usable, bioent, counts[0]>1, counts[1]>1, counts[2]>1))
#        else:
#            index = aspect_to_index[usable.go_aspect]
#            nodes.append(create_go_node(usable, bioent, index==0, index==1, index==2))
#    
#    edges = []
#    for biofact in level_one:
#        if biofact.bioconcept in usable_bios and biofact.bioentity in usable_bios:
#            edges.append(create_go_edge(biofact, biofact.bioentity, biofact.bioconcept))
#    
#    for biofact in level_two:
#        if biofact.bioconcept in usable_bios and biofact.bioentity in usable_bios and \
#        biofact.bioentity != bioent:
#            edges.append(create_go_edge(biofact, biofact.bioentity, biofact.bioconcept))
#    
#    return {'dataSchema':go_schema, 'data': {'nodes': nodes, 'edges': edges}, 
#            'disable_cellular':disable_cellular}
#    
#'''
#-------------------------------Utils---------------------------------------
#'''  
#def divide_goevidences(goevidences):
#    process_evidences = [evidence for evidence in goevidences if evidence.bioconcept.go_aspect == 'biological process']
#    function_evidences = [evidence for evidence in goevidences if evidence.bioconcept.go_aspect == 'molecular function']
#    component_evidences = [evidence for evidence in goevidences if evidence.bioconcept.go_aspect == 'cellular component']
#
#    return {'process':process_evidences, 'function':function_evidences, 'component':component_evidences}
#
#def divide_biofacts(biofacts):
#    process_biofacts = [biofact for biofact in biofacts if biofact.bioconcept.go_aspect == 'biological process']
#    function_biofacts = [biofact for biofact in biofacts if biofact.bioconcept.go_aspect == 'molecular function']
#    component_biofacts = [biofact for biofact in biofacts if biofact.bioconcept.go_aspect == 'cellular component']
#
#    return {'process':process_biofacts, 'function':function_biofacts, 'component':component_biofacts}
#  
#def get_id(bio):
#    return bio.type + str(bio.id)
