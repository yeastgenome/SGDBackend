from .models import DBSession
from model_new_schema.bioentity import create_bioentity_subclasses
from pyramid.config import Configurator
from sgd2.config import DBUSER, DBPASS, DBHOST, DBNAME, DBTYPE
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import model_new_schema



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)

    DBSession.configure(bind=engine)
    model_new_schema.Base.metadata.bind = engine
    create_bioentity_subclasses(DBSession)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    config.add_route('home', '/')
    config.add_route('my_sgd', '/my_sgd')
    config.add_route('help', '/help')
    config.add_route('about', '/about')

    config.scan()
    return config.make_wsgi_app()
