'''
Created on Aug 20, 2013

@author: kpaskov
'''
from backend import prepare_sgdbackend, prepare_perfbackend
import pytest

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
        help="run slow tests")
    parser.addoption("--model", action="store", default="perfbackend",
        help="Backend option: sgdbackend or perfbackend")

def pytest_runtest_setup(item):
    if 'slow' in item.keywords and not item.config.getoption("--runslow"):
        pytest.skip("need --runslow option to run")    

@pytest.fixture(scope="session")
def model(request):
    model_type = request.config.getoption("--model")
    if model_type == 'sgdbackend':
        return prepare_sgdbackend()[0]
    if model_type == 'perfbackend':
        return prepare_perfbackend()[0]
    raise Exception('No backend supplied.')