from src.sgd.convert.from_bud import basic_convert, remove_nones
from sqlalchemy.orm import joinedload

__author__ = 'kpaskov'


def allele_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import ExperimentProperty
    from src.sgd.model.bud.go import GorefDbxref

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(ExperimentProperty).filter(ExperimentProperty.type == 'Allele').all():
        if bud_obj.type == 'Allele':
            yield {'display_name': bud_obj.value,
                   'source': {'display_name': 'SGD'},
                   'bud_id':bud_obj.id,
                   'date_created': str(bud_obj.date_created),
                   'created_by': bud_obj.created_by}

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, allele_starter, 'allele', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
