__author__ = 'kpaskov'

import json
from src.sgd.model import curate
from src.sgd.backend.nex import SGDBackend
from src.sgd.backend.curate import CurateBackend
from src.sgd.convert import prepare_schema_connection, config

def compare_json_objects(obj_json1, obj_json2, verbose=False):
    are_equal = True
    if isinstance(obj_json1, dict) and isinstance(obj_json2, dict):
        for key1, value1 in obj_json1.iteritems():
            if key1 not in set(['id', 'link', 'format_name']):
                if key1 not in obj_json2:
                    if verbose:
                        print 'Missing: ', key1
                    are_equal = False
                else:
                    are_equal = are_equal and compare_json_objects(value1, obj_json2[key1], verbose=verbose)
    elif isinstance(obj_json1, list) and isinstance(obj_json2, list):
        for entry1 in obj_json1:
            found_match = False
            for entry2 in obj_json2:
                if compare_json_objects(entry1, entry2, verbose=False):
                    found_match = True
                    break
            if verbose and not found_match:
                'Missing: ', entry1
            are_equal = are_equal and found_match
    elif obj_json1 == obj_json2:
        pass
    else:
        if verbose:
            print 'Mismatch: ', obj_json1, obj_json2
        are_equal = False
    return are_equal


def remove_matches(obj_json1, obj_json2):
    if json.dumps(obj_json1, sort_keys=True) == json.dumps(obj_json2, sort_keys=True):
        return None

    elif isinstance(obj_json1, dict) and isinstance(obj_json2, dict):
        for key2, value2 in obj_json2.iteritems():
            if key2 in obj_json1:
                obj_json1[key2] = remove_matches(obj_json1[key2], value2)
        return obj_json1

    elif isinstance(obj_json1, list) and isinstance(obj_json2, list):
        str_entries2 = set(json.dumps(x, sort_keys=True) for x in obj_json2)
        return [x for x in obj_json1 if json.dumps(x, sort_keys=True) not in str_entries2]
    else:
        print 'Error'
        return None


sgdbackend = SGDBackend(config.NEX_DBTYPE, 'sgd-master-db:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)
curatebackend = CurateBackend(config.NEX_DBTYPE, 'curator-dev-db:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, None)
curate_session_maker = prepare_schema_connection(curate, config.NEX_DBTYPE, 'curator-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
curate_session = curate_session_maker()

for id, display_name, format_name in json.loads(curatebackend.get_all_objects('author', None, None, 'mini')):
    sgdresponse = sgdbackend.author(format_name)
    curateresponse = curatebackend.get_object('author', format_name)

    if sgdresponse is None:
        print 'Missing', format_name
    else:
        if not compare_json_objects(json.loads(sgdresponse), json.loads(curateresponse), verbose=True):
            print 'Mismatch', format_name
        else:
            print 'Match', format_name

curate_session.close()