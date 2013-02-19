from .models import DBSession
from jsonify.bioent_json import bioent_small, bioent_large, biorel_large, \
    reference_large, biocon_large, bioent_biocon_large, create_graph
from model_new_schema.bioconcept import Bioconcept, BioentBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Biorelation
from model_new_schema.reference import Reference
from model_new_schema.search import Typeahead
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
 


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

@view_config(route_name='search', renderer='templates/search.pt')
def search_view(request):
    try:
        search_str = request.matchdict['search_str'].upper()
        bioents = DBSession.query(Bioentity).join(Typeahead).filter(Typeahead.bio_type == 'BIOENT', func.upper(Typeahead.name) == search_str).all()
        json_bioents = [bioent_small(b) for b in bioents]
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'layout': site_layout(), 'page_title': 'Search Results', 'bioents': json_bioents}

@view_config(route_name='typeahead', renderer="json")
def typeahead_view(request):
    try:
        q = request.POST.items()[0][1].upper()
        possible = DBSession.query(Typeahead).filter(func.upper(Typeahead.name) == q).all()
        full_names = [p.full_name for p in possible]
        return full_names
    except DBAPIError:
        return ['Error']
    
@view_config(route_name='bioent_graph', renderer="json")
def bioent_graph_view(request):
    try:
        bioent_name = request.matchdict['bioent_name'].upper()
        bioent = DBSession.query(Bioentity).filter(func.upper(Bioentity.name)==bioent_name).first()
        graph = create_graph(bioent)
        return graph
    except DBAPIError:
        return ['Error']

@view_config(route_name='bioent', renderer='templates/bioent.pt')
def bioent_view(request):
    bioent_name = request.matchdict['bioent_name'].upper()
    
    bioent = DBSession.query(Bioentity).options(joinedload('bioent_biocons')).filter(func.upper(Bioentity.name)==bioent_name).first()
    json_bioent = bioent_large(bioent)
    return {'layout': site_layout(), 'page_title': json_bioent['basic_info']['name'], 'bioent': json_bioent}

@view_config(route_name='biorel', renderer='templates/biorel.pt')
def biorel_view(request):
    biorel_name = request.matchdict['biorel_name'].upper()
    biorel = DBSession.query(Biorelation).options(joinedload('biorel_evidences')).filter(func.upper(Biorelation.name)==biorel_name).first()
    json_biorel = biorel_large(biorel)
    return {'layout': site_layout(), 'page_title': json_biorel['basic_info']['name'], 'biorel': json_biorel}

@view_config(route_name='biocon', renderer='templates/biocon.pt')
def biocon_view(request):
    biocon_name = request.matchdict['biocon_name'].upper()
    biocon = DBSession.query(Bioconcept).options(joinedload('bioent_biocons')).filter(func.upper(Bioconcept.name)==biocon_name).first()
    json_biocon = biocon_large(biocon)
    return {'layout': site_layout(), 'page_title': json_biocon['basic_info']['name'], 'biocon': json_biocon}

@view_config(route_name='bioent_biocon', renderer='templates/bioent_biocon.pt')
def bioent_biocon_view(request):
    bioent_biocon_name = request.matchdict['bioent_biocon_name'].upper()
    bioent_biocon = DBSession.query(BioentBiocon).options(joinedload('evidences')).filter(func.upper(BioentBiocon.name)==bioent_biocon_name).first()
    json_bioent_biocon = bioent_biocon_large(bioent_biocon)
    return {'layout': site_layout(), 'page_title': json_bioent_biocon['basic_info']['name'], 'bioent_biocon': json_bioent_biocon}

@view_config(route_name='reference', renderer='templates/reference.pt')
def reference_view(request):
    pubmed_id = request.matchdict['pubmed_id']
    reference = DBSession.query(Reference).filter(Reference.pubmed_id == pubmed_id).first()
    json_reference = reference_large(reference)
    return {'layout': site_layout(), 'page_title': 'PMID ' + json_reference['basic_info']['pubmed_id'], 'ref': json_reference}

