'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import go_evidence_table_link
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent_biocons, get_go_evidence, get_biocon, get_bioent
from sgd2.views import site_layout
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
    return {'layout': site_layout(), 'page_title': biocon.name, 'biocon': biocon} 

@view_config(route_name='go_evidence', renderer='templates/go_evidence.pt')
def go_evidence(request):
    if 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        name = 'GO Evidence for ' + bioent.name
        description = 'Evidence for all GO terms associated with ' + bioent.name
        evidence_link = go_evidence_table_link(bioent=bioent)
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'description':description, 'gene_name':bioent.name_with_link,
                'biocon_name':'All', 'evidence_link':evidence_link, 'evidence_p_filename':bioent.name + '_go_process_evidence',
                'evidence_f_filename':bioent.name + '_go_function_evidence','evidence_c_filename': bioent.name + '_go_component_evidence',
                'go_graph_link':'/bioent/' + bioent.official_name + '/go_graph'}

    else:
        return Response(status_int=500, body='No Bioent specified.')

@view_config(route_name='go_overview_table', renderer='json')
def go_overview_table(request):
    if 'biocon_name' in request.GET:
        #Need a GO overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        bioent_biocons = get_bioent_biocons(biocon=biocon)
        return make_overview_tables(False, bioent_biocons) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        bioent_biocons = get_bioent_biocons(bioent=bioent)
        return make_overview_tables(True, bioent_biocons, False) 

    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')


@view_config(route_name='go_evidence_table', renderer='json')
def go_evidence_table(request):
    if 'biocon_name' in request.GET:
        #Need a GO overview table based on a biocon
        biocon_name = request.GET['biocon_name']
        biocon = get_biocon(biocon_name, 'GO')
        bioent_biocons = get_bioent_biocons(biocon=biocon)
        return make_evidence_tables(False, bioent_biocons) 
        
    elif 'bioent_name' in request.GET:
        #Need a GO overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        bioent_biocons = get_bioent_biocons(bioent=bioent)
        return make_evidence_tables(True, bioent_biocons) 
    
    else:
        return Response(status_int=500, body='No Bioent or Biocon specified.')

'''
-------------------------------Overview Table---------------------------------------
'''

def make_overview_tables(divided, bioent_biocons, include_comp=True):
    tables = {}
    
    goevidences = None
    if len(bioent_biocons) < 500:
        goevidences = get_go_evidence(bioent_biocons)

    if goevidences is not None and not include_comp:
        tables['computational'] = len(set([evidence.bioent_biocon for evidence in goevidences if evidence.annotation_type == 'computational']))
        goevidences = [evidence for evidence in goevidences if evidence.annotation_type != 'computational']
        
    if divided:
        tables['go_p'] = make_single_overview_table(bioent_biocons, goevidences, 'biological process')
        tables['go_f'] = make_single_overview_table(bioent_biocons, goevidences, 'molecular function')
        tables['go_c'] = make_single_overview_table(bioent_biocons, goevidences, 'cellular component')
    else:
        tables['aaData'] = make_single_overview_table(bioent_biocons, goevidences)
    return tables    

def make_single_overview_table(bioent_biocons, goevidences=None, namespace=None):
    if goevidences is not None:
        if namespace is not None:
            goevidences = [evidence for evidence in goevidences if evidence.bioent_biocon.bioconcept.go_aspect == namespace]
            
        evidence_map = dict([(evidence.id, evidence.bioent_biocon) for evidence in goevidences])
        return create_grouped_evidence_table(goevidences, evidence_map, make_overview_row)
    elif bioent_biocons is not None:
        if namespace is not None:
            bioent_biocons = [bioent_biocon for bioent_biocon in bioent_biocons if bioent_biocon.bioconcept.go_aspect == namespace]
        
        return create_simple_table(bioent_biocons, make_overview_row)  


def make_overview_row(bioent_biocon, evs_for_group=None, group_term=None):
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
        tables['go_p'] = make_single_evidence_table(goevidences, 'biological process')
        tables['go_f'] = make_single_evidence_table(goevidences, 'molecular function')
        tables['go_c'] = make_single_evidence_table(goevidences, 'cellular component')
    else:
        tables['aaData'] = make_single_evidence_table(goevidences)
        
    tables['reference'] = make_reference_list(goevidences)
        
    return tables    

def make_single_evidence_table(goevidences, namespace=None):
    if namespace is not None:
        goevidences = [evidence for evidence in goevidences if evidence.bioent_biocon.bioconcept.go_aspect == namespace]
            
    return create_simple_table(goevidences, make_evidence_row)

def make_evidence_row(goevidence): 
    bioent = goevidence.bioent_biocon.bioentity
    biocon = goevidence.bioent_biocon.bioconcept
    return [biocon.name_with_link, bioent.name_with_link, goevidence.go_evidence, goevidence.annotation_type, goevidence.qualifier, 
            goevidence.source, goevidence.reference.name_with_link]
  
