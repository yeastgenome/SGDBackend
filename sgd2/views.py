from model_new_schema.link_maker import LinkMaker
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent, get_reference
 
def site_layout():
    renderer = get_renderer("templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout

@view_config(route_name='home', renderer='templates/index.pt')
def home_view(request):
    return {'layout': site_layout(), 'page_title': 'SGD2.0'}

@view_config(route_name='my_sgd', renderer='templates/my_sgd.pt')
def my_sgd_view(request):
    return {'layout': site_layout(), 'page_title': 'My SGD'}

@view_config(route_name='help', renderer='templates/help.pt')
def help_view(request):
    return {'layout': site_layout(), 'page_title': 'Help'}

@view_config(route_name='about', renderer='templates/about.pt')
def about_view(request):
    return {'layout': site_layout(), 'page_title': 'About'}


@view_config(route_name='gene', renderer='templates/gene.pt')
def gene_view(request):
    bioent_name = request.matchdict['gene_name']
    bioent = get_bioent(bioent_name)
    if bioent is None:
        return Response(status_int=500, body='Gene could not be found.')
    return {'layout': site_layout(), 'page_title': bioent.name, 'bioent': bioent, 'link_maker':LinkMaker(bioent.name, bioent=bioent)}
  
@view_config(route_name='protein', renderer='templates/protein.pt')
def protein_view(request):
    bioent_name = request.matchdict['protein_name']
    bioent = get_bioent(bioent_name)
    if bioent is None:
        return Response(status_int=500, body='Protein could not be found.')
    return {'layout': site_layout(), 'page_title': bioent.name, 'bioent': bioent, 'link_maker':LinkMaker(bioent.name, bioent=bioent)}
 

@view_config(route_name='reference', renderer='templates/reference.pt')
def reference_view(request):
    ref_name = request.matchdict['pubmed_id']
    reference = get_reference(ref_name)   
    if reference is None:
            return Response(status_int=500, body='Reference could not be found.') 
    return {'layout': site_layout(), 'page_title': reference.name, 'ref': reference, 'link_maker':LinkMaker(reference.name, reference=reference)}