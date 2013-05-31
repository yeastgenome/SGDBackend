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
from utils.utils import create_simple_table

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
    elif 'reference_name' in request.GET:
        #Need a bioentevidence table based on a reference
        ref_name = request.GET['reference_name']
        ref_id = get_reference_id(ref_name)
        if ref_id is None:
            return Response(status_int=500, body='Reference could not be found.')
        bioentevidences = get_bioent_evidence(reference_id=ref_id)
        return make_evidence_table(bioentevidences) 
    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')
    
def make_evidence_table(bioentevidences):
    
    def f(bioentevidence):
        gene = bioentevidence.gene
        reference = bioentevidence.reference
        return [bioentevidence.topic, gene.name_with_link, reference.name_with_link]
        
    tables = {}
    tables['aaData'] = create_simple_table(bioentevidences, f) 
    return tables
