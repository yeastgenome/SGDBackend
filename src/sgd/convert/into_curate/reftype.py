from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'


def reftype_starter(bud_session_maker):
    from src.sgd.model.bud.reference import RefType
    bud_session = bud_session_maker()

    for old_reftype in bud_session.query(RefType).all():
        yield {'name': old_reftype.name,
               'source': {'name': old_reftype.source},
               'bud_id': old_reftype.id,
               'date_created': str(old_reftype.date_created),
               'created_by': old_reftype.created_by}

    bud_session.close()

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, reftype_starter, 'reftype', lambda x: x['name'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')