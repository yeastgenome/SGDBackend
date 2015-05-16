from src.sgd.convert.from_bud import basic_convert, remove_nones
from sqlalchemy.orm import joinedload

__author__ = 'kpaskov'


def enzyme_starter(bud_session_maker):
    from src.sgd.model.bud.general import Dbxref

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Dbxref).filter(Dbxref.dbxref_type == 'EC number').all():
        yield remove_nones({'display_name': bud_obj.dbxref_id,
               'source': {'display_name': bud_obj.source},
               'description': bud_obj.dbxref_name,
               'bud_id': bud_obj.id,
               'urls': [{'display_name': 'ExPASy',
                         'link': 'http://enzyme.expasy.org/EC/' + bud_obj.dbxref_id,
                         'source': {'display_name': 'ExPASy'},
                         'url_type': 'ExPASy'},
                        {'display_name': 'BRENDA',
                         'link': 'http://www.brenda-enzymes.org/php/result_flat.php4?ecno=' + bud_obj.dbxref_id,
                         'source': {'display_name': '-'},
                         'url_type': 'BRENDA'}],
               'date_created': str(bud_obj.date_created),
               'created_by': bud_obj.created_by})

    bud_session.close()

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, enzyme_starter, 'enzyme', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

