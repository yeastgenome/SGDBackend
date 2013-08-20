from sgdbackend import prep_sqlalchemy, prep_views
import pytest
import conftest

class PseudoRequest():
    def __init__(self, **kwargs):
        self.matchdict = kwargs
        
@pytest.fixture(scope="module")
def model():
    config = prep_sqlalchemy()
    prep_views(config)