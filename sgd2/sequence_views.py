'''
Created on Mar 23, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent, get_sequences

@view_config(route_name='sequence', renderer='json')
def sequence(request):
    if 'bioent_name' in request.GET:
        bioent_name = request.GET['bioent_name']
        strain_name = 'S288C'

        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        return get_sequences(bioent, strain_name)

    else:
        return Response(status_int=500, body='No Bioent or Strain specified.')