from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert

__author__ = 'sweng66'


def colleague_association_starter(bud_session_maker):
    from src.sgd.model.bud.colleague import ColleagueRelation
    from src.sgd.model.nex.colleague import Colleague

    bud_session = bud_session_maker()    
    nex_session = get_nex_session()

    bud_id_to_colleague_id = dict([(x.bud_id, x.id) for x in nex_session.query(Colleague).all()])

    for bud_obj in bud_session.query(ColleagueRelation).all():
        
        coll_id = bud_id_to_colleague_id.get(bud_obj.colleague_id)
        assoc_id = bud_id_to_colleague_id.get(bud_obj.associate_id)

        if coll_id is None or assoc_id is None:
            continue

        yield { "colleague_id": coll_id,
                "associate_id": assoc_id,
                "bud_id": bud_obj.id,
                "association_type": bud_obj.relationship_type,
                "source": { "display_name": "Direct submission"},
                "date_created": str(bud_obj.date_created),
                "created_by": bud_obj.created_by }

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, colleague_association_starter, 'colleague_association', lambda x: (x['colleague_id'], x['associate_id'], x['association_type']))
