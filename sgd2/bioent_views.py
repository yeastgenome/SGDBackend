'''
Created on May 31, 2013

@author: kpaskov
'''
from model_new_schema.link_maker import LinkMaker
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent, get_bioent_id, get_bioent_evidence, \
    get_reference_id
from sgd2.views import site_layout
from utils.utils import create_simple_table, make_reference_list

@view_config(route_name='gene', renderer='templates/gene.pt')
def gene_view(request):
    bioent_name = request.matchdict['gene_name']
    bioent = get_bioent(bioent_name)
    if bioent is None:
        return Response(status_int=500, body='Gene could not be found.')
    return {'layout': site_layout(), 'page_title': bioent.display_name, 'bioent': bioent, 'link_maker':LinkMaker(bioent.format_name, bioent=bioent)}
  
@view_config(route_name='protein', renderer='templates/protein.pt')
def protein_view(request):
    bioent_name = request.matchdict['protein_name']
    bioent = get_bioent(bioent_name)
    if bioent is None:
        return Response(status_int=500, body='Protein could not be found.')
    return {'layout': site_layout(), 'page_title': bioent.display_name, 'bioent': bioent, 'link_maker':LinkMaker(bioent.format_name, bioent=bioent)}
 
@view_config(route_name='bioent_evidence', renderer='templates/bioent_evidence.pt')
def phenotype_evidence(request):
    if 'bioent_name' in request.GET:
        #Need a bioent evidence table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        name = 'Litguide for ' + bioent.display_name
        name_with_link = 'Litguide for ' + bioent.name_with_link
        return {'layout': site_layout(), 'page_title': name, 'name':name, 'name_with_link':name_with_link, 'split':True,
                'link_maker':LinkMaker(bioent.format_name, bioent=bioent)}
    else:
        return Response(status_int=500, body='No Bioent specified.')

@view_config(route_name='bioent_overview_table', renderer='json')
def bioent_overview_table(request):
    if 'bioent_name' in request.GET:
        #Need a bioent overview table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent_id = get_bioent_id(bioent_name)
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioentevidences = get_bioent_evidence(bioent_id=bioent_id)
        return make_reference_list(bioentevidences) 
    elif 'reference_name' in request.GET:
        #Need a bioent overview table based on a reference
        ref_name = request.GET['reference_name']
        ref_id = get_reference_id(ref_name)
        if ref_id is None:
            return Response(status_int=500, body='Reference could not be found.')
        bioentevidences = get_bioent_evidence(reference_id=ref_id)
        return make_overview_table(bioentevidences) 
    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')

@view_config(route_name='bioent_evidence_table', renderer='json')
def bioent_evidence_table(request):
    if 'bioent_name' in request.GET:
        #Need a bioentevidence table based on a bioent
        bioent_name = request.GET['bioent_name']
        bioent_id = get_bioent_id(bioent_name)
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioentevidences = get_bioent_evidence(bioent_id=bioent_id)
        return make_evidence_table(bioentevidences) 
    else:
        return Response(status_int=500, body='No Bioent specified.')
    
def make_overview_table(bioentevidences):

    def f(bioentevidence):
        gene = bioentevidence.gene
        reference = bioentevidence.reference
        return [bioentevidence.topic, gene.name_with_link, reference.name_with_link]
        
    tables = {}
    tables['aaData'] = create_simple_table(bioentevidences, f) 
    return tables
    
def make_evidence_table(bioentevidences):
    primary_evs = [evidence for evidence in bioentevidences if evidence.topic=='Primary Literature']
    additional_evs = [evidence for evidence in bioentevidences if evidence.topic=='Additional Literature']
    review_evs = [evidence for evidence in bioentevidences if evidence.topic=='Reviews']
    
    tables = {}
    tables['primary'] = make_reference_list(primary_evs) 
    tables['additional'] = make_reference_list(additional_evs) 
    tables['reviews'] = make_reference_list(review_evs) 

    return tables
