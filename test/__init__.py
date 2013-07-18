from sgdbackend import prep_sqlalchemy, prep_views
import pytest

class PseudoRequest():
    def __init__(self, **kwargs):
        self.GET = kwargs
        
@pytest.fixture(scope="module")
def model():
    config = prep_sqlalchemy()
    prep_views(config)