'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import LinkMaker
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent_biocons, get_go_evidence, get_biocon, get_bioent, \
    get_reference, get_go_evidence_ref, get_related_bioent_biocons, \
    get_biocon_family, get_biocon_biocons
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
        description = 'Evidence for all GO terms associated with ' + bioent.name
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'description':description, 'gene_name':bioent.name_with_link,
                'biocon_name':'All', 'link_maker':LinkMaker(bioent.name, bioent=bioent)}

    else:
        return Response(status_int=500, body='No Bioent specified.')

@view_config(route_name='go_overview_table', renderer='json')
def go_overview_table(request):
    if 'biocon_name' in request.GET:
        #Need a GO overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        if biocon is None:
            return Response(status_int=500, body='Biocon could not be found.')
        bioent_biocons = get_bioent_biocons('GO', biocon=biocon)
        goevidences = get_go_evidence(bioent_biocons)
        return make_overview_tables(False, goevidences) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioent_biocons = get_bioent_biocons('GO', bioent=bioent)
        goevidences = get_go_evidence(bioent_biocons)
        return make_overview_tables(True, goevidences, False) 
    
    elif 'reference_name' in request.GET:
        #Need a GO overview table based on a reference
        ref_name = request.GET['reference_name']
        ref = get_reference(ref_name)
        if ref is None:
            return Response(status_int=500, body='Reference could not be found.')
        goevidences = get_go_evidence_ref(ref)
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
        bioent_biocons = get_bioent_biocons('GO', biocon=biocon)
        return make_evidence_tables(False, bioent_biocons) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioent_biocons = get_bioent_biocons('GO', bioent=bioent)
        return make_evidence_tables(True, bioent_biocons) 
    
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
        tables['computational'] = len(set([evidence.bioent_biocon for evidence in goevidences if evidence.annotation_type == 'computational']))
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
    evidence_map = dict([(evidence.id, evidence.bioent_biocon) for evidence in goevidences])
    return create_grouped_evidence_table(goevidences, evidence_map, make_overview_row)

def make_overview_row(bioent_biocon, evs_for_group, group_term):
    ev_codes = ''
    if evs_for_group is not None:
        evidence_codes = set([ev.go_evidence for ev in evs_for_group])
        ev_codes = ', '.join(sorted(evidence_codes))
        
    bioent = bioent_biocon.bioentity
    biocon = bioent_biocon.bioconcept
    return [biocon.name_with_link, bioent.name_with_link, bioent.description, ev_codes]
    
'''
-------------------------------Evidence Table---------------------------------------
'''
    
def make_evidence_tables(divided, bioent_biocons, include_comp=True):
    tables = {}
    goevidences = get_go_evidence(bioent_biocons)

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
    bioent = goevidence.bioent_biocon.bioentity
    biocon = goevidence.bioent_biocon.bioconcept
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
                'edges': [ { 'name': "label", 'type': "string" }, 
                          {'name':'link', 'type':'string'}]}

def create_go_node(obj, focus_node, f_include, p_include, c_include):
    sub_type = None
    if obj.type == 'BIOCONCEPT':
        sub_type = obj.go_aspect.upper()
    if obj == focus_node:
        sub_type = 'FOCUS'
    name = obj.name.replace(' ', '\n')
    return {'id':get_id(obj), 'label':name, 'link':obj.link, 'sub_type':sub_type, 'bio_type':obj.type,
            'f_include':f_include, 'p_include':p_include, 'c_include':c_include}

def create_go_edge(obj, source_obj, sink_obj):
    return { 'id': get_id(obj), 'target': get_id(source_obj), 'source': get_id(sink_obj), 'label': obj.name, 'link':obj.link}  

aspect_to_index = {'molecular function':0, 'biological process':1, 'cellular component':2}
def create_go_graph(bioent=None, biocon=None):
    
    if bioent is not None:
        level_one = get_bioent_biocons('GO', bioent=bioent)
        level_one = [bioent_biocon for bioent_biocon in level_one if bioent_biocon.use_in_graph == 'Y']

        biocon_ids = [bioent_biocon.biocon_id for bioent_biocon in level_one]
        level_two = get_related_bioent_biocons(biocon_ids)
    
    usable_bios = set()       
    usable_bios.add(bioent)
    usable_bios.update([bioent_biocon.bioconcept for bioent_biocon in level_one])
    
    bioent_to_edge_counts = {}
    for bioent_biocon in level_two:
        ent = bioent_biocon.bioentity
        con = bioent_biocon.bioconcept
        
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
        not_cellular_component = [bioent_biocon.bioentity for bioent_biocon in level_two 
                                  if bioent_biocon.bioconcept.go_aspect != 'cellular component' 
                                  and (bioent_to_edge_counts[bioent_biocon.bioentity][0] >1 
                                       or bioent_to_edge_counts[bioent_biocon.bioentity][1] > 1)]
        usable_bios.update(not_cellular_component)
        disable_cellular = True
         
    nodes = []  
    for usable in usable_bios:
        if usable.type == 'BIOENTITY':
            counts = bioent_to_edge_counts[usable]
            nodes.append(create_go_node(usable, bioent, counts[0]>1, counts[1]>1, counts[2]>1))
        else:
            index = aspect_to_index[usable.go_aspect]
            nodes.append(create_go_node(usable, bioent, index==0, index==1, index==2))
    
    edges = []
    for bioent_biocon in level_one:
        if bioent_biocon.bioconcept in usable_bios and bioent_biocon.bioentity in usable_bios:
            edges.append(create_go_edge(bioent_biocon, bioent_biocon.bioentity, bioent_biocon.bioconcept))
    
    for bioent_biocon in level_two:
        if bioent_biocon.bioconcept in usable_bios and bioent_biocon.bioentity in usable_bios and \
        bioent_biocon.bioentity != bioent:
            edges.append(create_go_edge(bioent_biocon, bioent_biocon.bioentity, bioent_biocon.bioconcept))
    
    return {'dataSchema':go_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'disable_cellular':disable_cellular}
    
'''
-------------------------------Utils---------------------------------------
'''  
def divide_goevidences(goevidences):
    process_evidences = [evidence for evidence in goevidences if evidence.bioent_biocon.bioconcept.go_aspect == 'biological process']
    function_evidences = [evidence for evidence in goevidences if evidence.bioent_biocon.bioconcept.go_aspect == 'molecular function']
    component_evidences = [evidence for evidence in goevidences if evidence.bioent_biocon.bioconcept.go_aspect == 'cellular component']

    return {'process':process_evidences, 'function':function_evidences, 'component':component_evidences}

def divide_bioent_biocons(bioent_biocons):
    process_bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.go_aspect == 'biological process']
    function_bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.go_aspect == 'molecular function']
    component_bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.go_aspect == 'cellular component']

    return {'process':process_bioent_biocons, 'function':function_bioent_biocons, 'component':component_bioent_biocons}
  
def get_id(bio):
    return bio.type + str(bio.id)
