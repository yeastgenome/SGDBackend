import pytest

from src.sgd.backend.perf import PerfBackend
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend import config


__author__ = 'kpaskov'

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
        help="run slow tests")
    parser.addoption("--model", action="store", default="perf",
        help="Backend option: nex or perf")

def pytest_runtest_setup(item):
    if 'slow' in item.keywords and not item.config.getoption("--runslow"):
        pytest.skip("need --runslow option to run")

@pytest.fixture(scope="session")
def model(request):
    model_type = request.config.getoption("--model")
    if model_type == 'nex':
        return SGDBackend(config.DBTYPE, config.NEX_DBHOST, config.DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.sgdbackend_log_directory)
    if model_type == 'perf':
        return PerfBackend(config.DBTYPE, config.PERF_DBHOST, config.DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, config.perfbackend_log_directory)
    raise Exception('No backend supplied.')