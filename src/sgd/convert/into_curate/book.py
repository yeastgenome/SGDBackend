from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kpaskov'

def book_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Book
    bud_session = bud_session_maker()

    for old_book in bud_session.query(Book).all():
        yield remove_nones({
            'source': {'name': 'PubMed'},
            'title': old_book.title,
            'publisher': old_book.publisher,
            'bud_id': old_book.id,
            'volume_title': old_book.volume_title,
            'total_pages': old_book.total_pages,
            'publisher_location': old_book.publisher_location,
            'isbn': old_book.isbn,
            'date_created': str(old_book.date_created),
            'created_by': old_book.created_by})

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, book_starter, 'book', lambda x: (None if 'title' not in x else x['title'], None if 'volume_title' not in x else x['volume_title']))


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

