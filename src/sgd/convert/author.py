from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def author_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Author
    bud_session = bud_session_maker()

    for author in bud_session.query(Author).all():
        yield {'display_name': author.name,
               'source': {'display_name': 'PubMed'},
               'bud_id': author.id,
               'date_created': str(author.date_created),
               'created_by': author.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, author_starter, 'author', lambda x: x['display_name'])

