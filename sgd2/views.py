from .models import DBSession
from jsonify.large import phenoevidence_large, allele_large, \
    interevidence_large
from jsonify.small import bioent_small
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence, Allele
from model_new_schema.search import Typeahead
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
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
    


@view_config(route_name='evidence', renderer='templates/evidence.pt')
def evidence_view(request):
    evidence_id = request.matchdict['evidence_id']
    evidence = DBSession.query(Evidence).filter(Evidence.id == evidence_id).first()
    if evidence.evidence_type == 'PHENOTYPE_EVIDENCE':
        json_evidence = phenoevidence_large(evidence)
    else:
        json_evidence = interevidence_large(evidence)
    return {'layout': site_layout(), 'page_title': 'Evidence ' + str(evidence_id), 'evidence': json_evidence}

@view_config(route_name='allele', renderer='templates/allele.pt')
def allele_view(request):
    allele_name = request.matchdict['allele_name']
    allele = DBSession.query(Allele).filter(Allele.name == allele_name).first()
    json_allele = allele_large(allele)
    return {'layout': site_layout(), 'page_title': allele_name, 'allele': json_allele}

