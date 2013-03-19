'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import LinkMaker
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent_biocons, get_go_evidence, get_biocon, get_bioent, \
    get_reference, get_go_evidence_ref
from sgd2.views import site_layout
from utils.graph import create_go_graph
from utils.utils import create_grouped_evidence_table, create_simple_table, \
    make_reference_list


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
  
