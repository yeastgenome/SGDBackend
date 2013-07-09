from pyramid.response import Response
from pyramid.view import view_config
from query import get_chemical
from query.query_biocon import get_biocon
from query.query_bioent import get_bioent


@view_config(route_name='bioent', renderer='json')
def bioent(request):
    bioent_name = request.matchdict['bioent']
    bioent_type = request.matchdict['bioent_type'].upper()
    bioent = get_bioent(bioent_name, bioent_type)
    if bioent is None:
        return Response(status_int=500, body='Bioent could not be found.')
        
    bioent_json = {
                    'format_name': bioent.format_name,
                    'display_name': bioent.display_name, 
                    'name_with_link': bioent.name_with_link,
                    }
    return bioent_json

@view_config(route_name='biocon', renderer='json')
def biocon(request):
    biocon_name = request.matchdict['biocon']
    biocon_type = request.matchdict['biocon_type'].upper()
    biocon = get_biocon(biocon_name, biocon_type)
    if biocon is None:
        return Response(status_int=500, body='Biocon could not be found.')
        
    biocon_json = {
                    'format_name': biocon.format_name,
                    'display_name': biocon.display_name, 
                    'name_with_link': biocon.name_with_link,
                    }
    return biocon_json

@view_config(route_name='chemical', renderer='json')
def chemical(request):
    chemical_name = request.matchdict['chemical']
    chemical = get_chemical(chemical_name)
    if chemical is None:
        return Response(status_int=500, body='Chemical could not be found.')
    
    chemical_json = {
                     'format_name': chemical.format_name,
                     'display_name': chemical.display_name,
                     'name_with_link': chemical.name_with_link,
                     'aliases': chemical.alias_str
                     }
    return chemical_json



