__author__ = 'kpaskov'

import json
from src.sgd.model import perf
from src.sgd.backend.nex import SGDBackend
from src.sgd.convert import prepare_schema_connection, config

def compare_json_objects(obj_json1, obj_json2):
    s1 = json.dumps(obj_json1, sort_keys=True, indent=4)
    s2 = json.dumps(obj_json2, sort_keys=True, indent=4)
    print s1
    print s2
    return s1 == s2


backend1 = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)
backend2 = SGDBackend(config.NEX_DBTYPE, 'curator-dev-db:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)

perf_session = perf_session_maker()
from src.sgd.model.perf.core import Author
for author in perf_session.query(Author).limit(10).all():
    obj_json1 = json.loads(author.json)
    obj_json2 = json.loads(nex_backend.get_object('author', obj_json1['format_name']))


    print obj_json1['format_name'], compare_json_objects(obj_json1, obj_json2)