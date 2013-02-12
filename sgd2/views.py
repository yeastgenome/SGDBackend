from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import DBSession
from model_new_schema.bioentity import Bioentity

@view_config(route_name='home', renderer='templates/index.pt')
def home_view(request):
    try:
        one = DBSession.query(Bioentity).filter(Bioentity.id == 19357).first()
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'SGD2'}

@view_config(route_name='my_sgd', renderer='templates/my_sgd.pt')
def my_sgd_view(request):
    try:
        one = DBSession.query(Bioentity).filter(Bioentity.id == 19357).first()
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'SGD2'}

@view_config(route_name='help', renderer='templates/help.pt')
def help_view(request):
    try:
        one = DBSession.query(Bioentity).filter(Bioentity.id == 19357).first()
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'SGD2'}

@view_config(route_name='about', renderer='templates/about.pt')
def about_view(request):
    try:
        one = DBSession.query(Bioentity).filter(Bioentity.id == 19357).first()
    except DBAPIError:
        return Response("Error.", content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'SGD2'}
