from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'


def author_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Author
    bud_session = bud_session_maker()

    for old_author in bud_session.query(Author).all():
        yield {'name': old_author.name,
               'source': {'name': 'PubMed'},
               'bud_id': old_author.id,
               'date_created': str(old_author.date_created),
               'created_by': old_author.created_by}

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, author_starter, 'author', lambda x: x['name'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

