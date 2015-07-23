from src.sgd.convert import basic_convert, remove_nones

__author__ = 'kpaskov'
## updated by sweng66

def book_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Book
    bud_session = bud_session_maker()

    for old_book in bud_session.query(Book).all():
        yield remove_nones({
            'source': {'display_name': 'SGD'},
            'display_name': old_book.title,
            'title': old_book.title,
            'publisher': old_book.publisher,
            'bud_id': old_book.id,
            'volume_title': old_book.volume_title,
            'total_pages': old_book.total_pages,
            'isbn': old_book.isbn,
            'date_created': str(old_book.date_created),
            'created_by': old_book.created_by})

    bud_session.close()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, book_starter, 'book', lambda x: (x['title'], None if 'volume_title' not in x else x['volume_title']))



