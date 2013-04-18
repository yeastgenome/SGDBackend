'''
Created on Mar 19, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query import search, typeahead
from sgd2.views import site_layout
from sqlalchemy.exc import DBAPIError

@view_config(route_name='search', renderer='templates/search.pt')
def search_view(request):
    try:
        search_str = request.matchdict['search_str'].upper()
        bioents = search(search_str)
        from_name = []
        from_full_name = []
        other = []
        for bioent in bioents:
            if bioent.name.startswith(search_str):
                from_name.append(bioent)
            elif bioent.official_name.startswith(search_str):
                from_full_name.append(bioent)
            else:
                other.append(bioent)
        sorted_bioents = []
        sorted_bioents.extend(sorted(from_name, key=lambda x:x.name))
        sorted_bioents.extend(sorted(from_full_name, key=lambda x:x.name))
        sorted_bioents.extend(sorted(other, key=lambda x:x.name))
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'layout': site_layout(), 'page_title': 'Search Results', 'bioents': sorted_bioents}

@view_config(route_name='typeahead', renderer="json")
def typeahead_view(request):
    try:
        search_str = request.POST.items()[0][1].upper()
        possible = typeahead(search_str)
        full_names = [p.full_name for p in possible]
        return sorted(full_names)
    except DBAPIError:
        return ['Error']
    
    