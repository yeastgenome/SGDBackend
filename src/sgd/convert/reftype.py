from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def reftype_starter(bud_session_maker):
    from src.sgd.model.bud.reference import RefType
    bud_session = bud_session_maker()

    for reftype in bud_session.query(RefType).all():
        yield {'display_name': reftype.name,
               'source': {'display_name': reftype.source},
               'bud_id': reftype.id,
               'date_created': str(reftype.date_created),
               'created_by': reftype.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reftype_starter, 'reftype', lambda x: x['display_name'])

