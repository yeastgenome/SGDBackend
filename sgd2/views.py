from model_new_schema.link_maker import LinkMaker
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent, get_reference, get_author
 
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

@view_config(route_name='author', renderer='templates/author.pt')
def author_view(request):
    author_name = request.matchdict['author_name'].replace('_', ' ')
    author = get_author(author_name)
    if author is None:
            return Response(status_int=500, body='Author could not be found.') 
    return {'layout': site_layout(), 'page_title': author.name, 'author': author}

@view_config(route_name='download_graph')
def download_graph_view(request):
    file_type = request.matchdict['file_type']
    headers = request.response.headers
    if file_type == 'png':
        headers['Content-Type'] = 'image/png'
    elif file_type == 'pdf':
        headers['Content-Type'] = 'application/pdf'
    elif file_type == 'svg':
        headers['Content-Type'] = 'image/svg+xml'
    elif file_type == 'xml':
        headers['Content-Type'] = 'text/xml'
    elif file_type == 'txt':
        headers['Content-Type'] = 'text/plain'
    
    request.response.body = request.body
        
    headers['Content-Disposition'] = str('attachment; filename=network.' + file_type)
    headers['Content-Description'] = 'File Transfer'
    return request.response



