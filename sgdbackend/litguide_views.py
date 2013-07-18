'''
Created on May 31, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query.query_bioent import get_bioent_id
from query.query_evidence import get_bioent_evidence
from query.query_reference import get_reference_id
from sgdbackend.utils import make_reference_list, \
    make_reference_list_order_by_date

@view_config(route_name='bioent_overview_table', renderer='jsonp') 
def bioent_overview_table(request):
    if 'bioent' in request.GET:
        #Need a bioent overview table based on a bioent
        bioent_name = request.GET['bioent']
        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioentevidences = get_bioent_evidence(bioent_id=bioent_id)
        primary_bioentevidences = [evidence for evidence in bioentevidences if evidence.topic=='Primary Literature']
        return make_reference_list(primary_bioentevidences) 
    elif 'reference' in request.GET:
        #Need a bioent overview table based on a reference
        ref_name = request.GET['reference']
        ref_id = get_reference_id(ref_name)
        if ref_id is None:
            return Response(status_int=500, body='Reference could not be found.')
        bioentevidences = get_bioent_evidence(reference_id=ref_id)
        primary = ', '.join([evidence.bioentity.name_with_link for evidence in bioentevidences if evidence.topic=='Primary Literature'])
        additional = ', '.join([evidence.bioentity.name_with_link for evidence in bioentevidences if evidence.topic=='Additional Literature'])
        review = ', '.join([evidence.bioentity.name_with_link for evidence in bioentevidences if evidence.topic=='Reviews'])
        return {'primary': primary, 'additional': additional, 'review': review}
    else:
        return Response(status_int=500, body='No Bioent or Reference specified.')

@view_config(route_name='bioent_evidence_table', renderer='jsonp')
def bioent_evidence_table(request):
    if 'bioent' in request.GET:
        #Need a bioentevidence table based on a bioent
        bioent_name = request.GET['bioent']
        bioent_id = get_bioent_id(bioent_name, 'LOCUS')
        if bioent_id is None:
            return Response(status_int=500, body='Bioent could not be found.')
        bioentevidences = get_bioent_evidence(bioent_id=bioent_id)
        return make_evidence_table(bioentevidences) 
    else:
        return Response(status_int=500, body='No Bioent specified.')
    
def make_evidence_table(bioentevidences):
    primary_evs = [evidence for evidence in bioentevidences if evidence.topic=='Primary Literature']
    additional_evs = [evidence for evidence in bioentevidences if evidence.topic=='Additional Literature']
    review_evs = [evidence for evidence in bioentevidences if evidence.topic=='Reviews']
    
    tables = {}
    tables['primary'] = make_reference_list_order_by_date(primary_evs) 
    tables['additional'] = make_reference_list_order_by_date(additional_evs) 
    tables['reviews'] = make_reference_list_order_by_date(review_evs) 

    return tables
