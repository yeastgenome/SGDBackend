from src.sgd.convert.from_bud import basic_convert

__author__ = 'kpaskov'

def book_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Book
    bud_session = bud_session_maker()

    for old_book in bud_session.query(Book).all():
        yield {'source': {'display_name': 'PubMed'},
               'title': old_book.title,
               'volume_title': old_book.volume_title,
               'isbn': old_book.isbn,
               'total_pages': old_book.total_pages,
               'publisher': old_book.publisher,
               'publisher_location': old_book.publisher_location,
               'bud_id': old_book.id,
               'date_created': str(old_book.date_created),
               'created_by': old_book.created_by}

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, book_starter, 'book', lambda x: (x['title'], x['volume_title']))


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

