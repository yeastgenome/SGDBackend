__author__ = 'kpaskov'
import json
from src.sgd.convert.transformers import make_file_starter

def book_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Book
    bud_session = bud_session_maker()

    for old_book in bud_session.query(Book).all():
        yield {'source': {'format_name': 'PubMed'},
               'title': old_book.title,
               'volume_title': old_book.volume_title,
               'isbn': old_book.isbn,
               'total_pages': old_book.total_pages,
               'publisher': old_book.publisher,
               'publisher_location': old_book.publisher_location,
               'date_created': str(old_book.date_created),
               'created_by': old_book.created_by}

    bud_session.close()

if __name__ == '__main__':

    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, 'curator-dev-db', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    accumulated_status = dict()
    for obj_json in book_starter(bud_session_maker):
        output = curate_backend.update_object('book', None, obj_json)
        status = json.loads(output)['status']
        if status == 'Error':
            print output
        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1
    print 'convert.book', accumulated_status

