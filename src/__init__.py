from src.sgd.backend import prepare_backend

__author__ = 'kpaskov'

def nexbackend(global_config, **configs):
    config = prepare_backend('nex')
    return config.make_wsgi_app()

def perfbackend(global_config, **configs):
    config = prepare_backend('perf')
    return config.make_wsgi_app()

def curatebackend(global_config, **configs):
    config = prepare_backend('curate')
    return config.make_wsgi_app()