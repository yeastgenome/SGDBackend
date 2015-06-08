import re
import json
import datetime

__author__ = 'kpaskov'


def basic_convert(bud_db, nex_db, starter, class_name, key_f):
    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    start = datetime.datetime.now()
    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, bud_db, config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, nex_db, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    already_seen = set()

    accumulated_status = dict()
    warnings_count = 0
    for obj_json in starter(bud_session_maker):
        key = key_f(obj_json)
        print key
        if key in already_seen:
            status = 'Duplicate'
        else:
            response = curate_backend.add_object(class_name, obj_json, update_ok=True)
            status = response['status']
            warnings_count += len(response['warnings'])
            already_seen.add(key)

        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1

    # Delete objects not seen
    accumulated_status['Delete'] = 0
    for obj_json in curate_backend.get_all_objects(class_name, {'size': 'small'}):
        if key_f(obj_json) not in already_seen:
            curate_backend.delete_object(class_name, obj_json['id'])
            accumulated_status['Delete'] += 1

    end = datetime.datetime.now()
    print end.date(), 'convert.from_bud.' + class_name, accumulated_status, 'Warnings', warnings_count, 'Start-End/Duration:', \
        datetime.datetime.strftime(start, '%X') + '-' + datetime.datetime.strftime(end, '%X') + '/' + str(end-start)

def remove_nones(obj_json):
    to_be_deleted = set()
    for key, value in obj_json.iteritems():
        if value is None:
            to_be_deleted.add(key)
    for key in to_be_deleted:
        del obj_json[key]
    return obj_json