__author__ = 'kpaskov'
import json
from src.sgd.convert.transformers import make_file_starter

def author_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Author
    bud_session = bud_session_maker()

    for old_author in bud_session.query(Author).all():
        yield {'display_name': old_author.name,
               'source': {'format_name': 'PubMed'},
               'bud_id': old_author.id,
               'date_created': str(old_author.date_created),
               'created_by': old_author.created_by}

    bud_session.close()

def convert(bud_db, nex_db):
    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, bud_db, config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, nex_db, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    accumulated_status = dict()
    for obj_json in author_starter(bud_session_maker):
        output = curate_backend.add_object('author', obj_json, update_ok=True)
        status = json.loads(output)['status']
        if status == 'Error':
            print output
        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1
    print 'convert.author', accumulated_status

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

