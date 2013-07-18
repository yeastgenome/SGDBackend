'''
Created on Jul 16, 2013

@author: kpaskov
'''
from go_enrichment import go_enrichment
from pyramid.view import view_config
from pyramid.response import Response

@view_config(route_name='go_enrichment', renderer="jsonp")
def go_enrichment_view(request):
    bioent_ids_str = request.GET['bioent_ids']
    bioent_ids = [int(x) for x in bioent_ids_str[1:len(bioent_ids_str)-1].split(',')]
    results = go_enrichment(bioent_ids)
    if results is None:
        return Response(status_int=500, body='Bioents could not be found.')    
    return results