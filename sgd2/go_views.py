'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import LinkMaker
from pyramid.response import Response
from pyramid.view import view_config
from query import get_biofacts, get_go_evidence, get_biocon, get_bioent, \
    get_reference, get_related_biofacts, get_biocon_family, get_biocon_biocons, \
    get_biocon_id
from sgd2.views import site_layout
from utils.utils import create_grouped_evidence_table, create_simple_table, \
    make_reference_list
import math


'''
-------------------------------Views---------------------------------------
'''
@view_config(route_name='go', renderer='templates/go.pt')
def go(request):
    biocon_name = request.matchdict['biocon_name']
    biocon = get_biocon(biocon_name, 'GO')
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
    return {'layout': site_layout(), 'page_title': biocon.name, 'biocon': biocon, 'link_maker':LinkMaker(biocon.name, biocon=biocon)} 

@view_config(route_name='go_evidence', renderer='templates/go_evidence.pt')
def go_evidence(request):
    if 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        name = 'GO Evidence for ' + bioent.name
        name_with_link = 'GO Evidence for ' + bioent.name_with_link
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'name_with_link':name_with_link, 'split':True,
                'link_maker':LinkMaker(bioent.name, bioent=bioent)}
    elif 'biocon_name' in request.GET:
        #Need a GO overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        
        name = 'Evidence for GO Term:<br>' + biocon.name
        name_with_link = 'Evidence for GO Term:<br>' + biocon.name_with_link
       
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'name_with_link':name_with_link, 'split':False,
                'link_maker':LinkMaker(biocon.name, biocon=biocon)}
    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')

@view_config(route_name='go_overview_table', renderer='json')
def go_overview_table(request):
    if 'biocon_name' in request.GET:
        #Need a GO overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon_id = get_biocon_id(biocon_name, 'GO')
        if biocon_id is None:
            return Response(status_int=500, body='Biocon could not be found.')
        goevidences = get_go_evidence(biocon_id=biocon_id)
        return make_overview_tables(False, goevidences) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        goevidences = get_go_evidence(bioent_id=bioent.id)
        return make_overview_tables(True, goevidences, False) 
    
    elif 'reference_name' in request.GET:
        #Need a GO overview table based on a reference
        ref_name = request.GET['reference_name']
        ref = get_reference(ref_name)
        if ref is None:
            return Response(status_int=500, body='Reference could not be found.')
        goevidences = get_go_evidence(reference_id=ref.id)
        return make_overview_tables(False, goevidences, True) 

    else:
        return Response(status_int=500, body='No Bioent or Biocon or Reference specified.')


@view_config(route_name='go_evidence_table', renderer='json')
def go_evidence_table(request):
    if 'biocon_name' in request.GET:
        #Need a GO overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        evidences = get_go_evidence(biocon_id=biocon.id)
        return make_evidence_tables(False, evidences) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        evidences = get_go_evidence(bioent_id=bioent.id)
        return make_evidence_tables(True, evidences) 
    
    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')
    
@view_config(route_name='go_graph', renderer="json")
def go_graph(request):
    if 'biocon_name' in request.GET:
        #Need a GO graph based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        return create_go_graph(biocon=biocon)
  
    elif 'bioent_name' in request.GET:
        #Need a GO graph based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        return create_go_graph(bioent=bioent)

    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')
    
@view_config(route_name='go_ontology_graph', renderer="json")
def go_ontology_graph(request):
    if 'biocon_name' in request.GET:
        #Need a GO ontology graph based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        return create_go_ontology_graph(biocon=biocon)

    else:
        return Response(status_int=500, body='No Biocon specified.')

'''
-------------------------------Overview Table---------------------------------------
'''

def make_overview_tables(divided, goevidences, include_comp=True):
    tables = {}
    
    if not include_comp:
        tables['computational'] = len(set([(evidence.bioent_id, evidence.biocon_id) for evidence in goevidences if evidence.annotation_type == 'computational']))
        goevidences = [evidence for evidence in goevidences if evidence.annotation_type != 'computational']
        
    if divided:
        divided_goevidences = divide_goevidences(goevidences)
        
        tables['go_p'] = make_single_overview_table(divided_goevidences['process'])
        tables['go_f'] = make_single_overview_table(divided_goevidences['function'])
        tables['go_c'] = make_single_overview_table(divided_goevidences['component'])
    else:
        tables['aaData'] = make_single_overview_table(goevidences)
    return tables    

def make_single_overview_table(goevidences):
    evidence_map = dict([(evidence.id, (evidence.bioentity, evidence.goterm)) for evidence in goevidences])
    return create_grouped_evidence_table(goevidences, evidence_map, make_overview_row)

def make_overview_row(evs_for_group, group_term):
    ev_codes = ''
    if evs_for_group is not None:
        evidence_codes = set([ev.go_evidence for ev in evs_for_group])
        ev_codes = ', '.join(sorted(evidence_codes))
        
    bioent = group_term[0]
    biocon = group_term[1]
    return [biocon.name_with_link, bioent.name_with_link, bioent.description, ev_codes]
    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, goevidences, include_comp=True):
    tables = {}

    if not include_comp:
        goevidences = [evidence for evidence in goevidences if evidence.annotation_type != 'computational']
        tables['computational'] = len([evidence for evidence in goevidences if evidence.annotation_type == 'computational'])
        
    if divided:
        divided_evidences = divide_goevidences(goevidences)
        tables['go_p'] = create_simple_table(divided_evidences['process'], make_evidence_row)
        tables['go_f'] = create_simple_table(divided_evidences['function'], make_evidence_row)
        tables['go_c'] = create_simple_table(divided_evidences['component'], make_evidence_row)
    else:
        tables['aaData'] = create_simple_table(goevidences, make_evidence_row)
        
    tables['reference'] = make_reference_list(goevidences)
        
    return tables    

def make_evidence_row(goevidence): 
    bioent = goevidence.bioentity
    biocon = goevidence.goterm
    reference = ''
    if goevidence.reference is not None:
        reference = goevidence.reference.name_with_link
    return [biocon.name_with_link, bioent.name_with_link, goevidence.go_evidence, goevidence.annotation_type, goevidence.qualifier, 
            goevidence.source, reference]

'''
------------------------------GO Ontology Graph-----------------------------
'''
go_ontology_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'bio_type', 'type':'string'},
                         {'name':'sub_type', 'type':'string'},
                         {'name':'child', 'type':'boolean'},
                         {'name':'direct_gene_count', 'type':'integer'}],
                'edges': [{'name': "directed", 'type': "boolean", 'defValue': True}]}

def create_go_ontology_node(obj, focus_node, child):
    sub_type = obj.go_aspect.upper()
    direct_gene_count = obj.direct_gene_count
    if direct_gene_count == 0:
        sub_type = 'NO_GENES'
    if obj == focus_node:
        sub_type = 'FOCUS'
    name = obj.name.replace(' ', '\n')
    size = 2*int(math.ceil(math.sqrt(direct_gene_count)))
    return {'id':'BIOCONCEPT' + str(obj.id), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type, 
            'child':child, 'direct_gene_count':size}

def create_go_ontology_edge(biocon_biocon):
    return { 'id': 'BIOCON_BIOCON' + str(biocon_biocon.id), 'source': 'BIOCONCEPT' + str(biocon_biocon.parent_biocon_id), 'target': 'BIOCONCEPT' + str(biocon_biocon.child_biocon_id)}  

    
def create_go_ontology_graph(biocon):
    
    biocon_family = get_biocon_family(biocon)
    child_ids = biocon_family['child_ids']
    nodes = [create_go_ontology_node(b, biocon, b.id in child_ids) for b in biocon_family['family']]
    edges = [create_go_ontology_edge(e) for e in get_biocon_biocons(biocon_family['all_ids'])]
        
    return {'dataSchema':go_ontology_schema, 'data': {'nodes': nodes, 'edges': edges}, 'has_children':len(child_ids)>0}
 
'''
------------------------------GO Graph-----------------------------
'''

go_schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'bio_type', 'type':'string'},
                         {'name':'sub_type', 'type':'string'},
                         {'name':'f_include', 'type':'boolean'},
                         {'name':'p_include', 'type':'boolean'},
                         {'name':'c_include', 'type':'boolean'}],
                'edges': []}

def create_go_node(obj, focus_node, f_include, p_include, c_include):
    sub_type = None
    if obj.type == 'GO':
        sub_type = obj.go_aspect.upper()
    if obj == focus_node:
        sub_type = 'FOCUS'
    name = obj.name.replace(' ', '\n')
    return {'id':get_id(obj), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type,
            'f_include':f_include, 'p_include':p_include, 'c_include':c_include}

def create_go_edge(obj, source_obj, sink_obj):
    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj),}  

aspect_to_index = {'molecular function':0, 'biological process':1, 'cellular component':2}
def create_go_graph(bioent=None, biocon=None):
    
    if bioent is not None:
        level_one = get_biofacts('GO', bioent=bioent)
        level_one = [biofact for biofact in level_one if biofact.use_in_graph == 'Y']

        biocon_ids = [biofact.biocon_id for biofact in level_one]
        level_two = get_related_biofacts(biocon_ids, 'GO')
    
    usable_bios = set()       
    usable_bios.add(bioent)
    usable_bios.update([biofact.bioconcept for biofact in level_one])
    
    bioent_to_edge_counts = {}
    for biofact in level_two:
        ent = biofact.bioentity
        con = biofact.bioconcept
        
        index = aspect_to_index[con.go_aspect]
            
        if ent in bioent_to_edge_counts:
            bioent_to_edge_counts[ent][index] = bioent_to_edge_counts[ent][index] + 1
        else:
            bioent_to_edge_counts[ent] = [0, 0, 0]
            bioent_to_edge_counts[ent][index] = 1
       
    more_usable_bios = [bio for bio in bioent_to_edge_counts.keys() if sum(bioent_to_edge_counts[bio]) > 1]
    if len(more_usable_bios) < 150:
        usable_bios.update(more_usable_bios)
        disable_cellular = False
    else:
        usable_bios.difference_update([biocon for biocon in usable_bios if biocon.type == 'BIOENTITY' or biocon.go_aspect == 'cellular component'])
        not_cellular_component = [biofact.bioentity for biofact in level_two 
                                  if biofact.bioconcept.go_aspect != 'cellular component' 
                                  and (bioent_to_edge_counts[biofact.bioentity][0] >1 
                                       or bioent_to_edge_counts[biofact.bioentity][1] > 1)]
        usable_bios.update(not_cellular_component)
        disable_cellular = True
         
    nodes = []  
    for usable in usable_bios:
        if usable.type == 'GENE':
            counts = bioent_to_edge_counts[usable]
            nodes.append(create_go_node(usable, bioent, counts[0]>1, counts[1]>1, counts[2]>1))
        else:
            index = aspect_to_index[usable.go_aspect]
            nodes.append(create_go_node(usable, bioent, index==0, index==1, index==2))
    
    edges = []
    for biofact in level_one:
        if biofact.bioconcept in usable_bios and biofact.bioentity in usable_bios:
            edges.append(create_go_edge(biofact, biofact.bioentity, biofact.bioconcept))
    
    for biofact in level_two:
        if biofact.bioconcept in usable_bios and biofact.bioentity in usable_bios and \
        biofact.bioentity != bioent:
            edges.append(create_go_edge(biofact, biofact.bioentity, biofact.bioconcept))
    
    return {'dataSchema':go_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'disable_cellular':disable_cellular}
    
'''
-------------------------------Utils---------------------------------------
'''  
def divide_goevidences(goevidences):
    process_evidences = [evidence for evidence in goevidences if evidence.goterm.go_aspect == 'biological process']
    function_evidences = [evidence for evidence in goevidences if evidence.goterm.go_aspect == 'molecular function']
    component_evidences = [evidence for evidence in goevidences if evidence.goterm.go_aspect == 'cellular component']

    return {'process':process_evidences, 'function':function_evidences, 'component':component_evidences}

def divide_biofacts(biofacts):
    process_biofacts = [biofact for biofact in biofacts if biofact.bioconcept.go_aspect == 'biological process']
    function_biofacts = [biofact for biofact in biofacts if biofact.bioconcept.go_aspect == 'molecular function']
    component_biofacts = [biofact for biofact in biofacts if biofact.bioconcept.go_aspect == 'cellular component']

    return {'process':process_biofacts, 'function':function_biofacts, 'component':component_biofacts}
  
def get_id(bio):
    return bio.type + str(bio.id)
