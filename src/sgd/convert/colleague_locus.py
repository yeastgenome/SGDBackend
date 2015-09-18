from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def colleague_locus_starter(bud_session_maker):
    from src.sgd.model.bud.colleague import ColleagueFeature
    from src.sgd.model.nex.colleague import Colleague
    from src.sgd.model.nex.locus import Locus

    bud_session = bud_session_maker()    
    nex_session = get_nex_session()

    bud_id_to_colleague_id = dict([(x.bud_id, x.id) for x in nex_session.query(Colleague).all()])
    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])

    for bud_obj in bud_session.query(ColleagueFeature).all():
        
        coll_id = bud_id_to_colleague_id.get(bud_obj.colleague_id)
        locus_id = bud_id_to_locus_id.get(bud_obj.feature_id)

        if coll_id is None or locus_id is None:
            continue

        yield { "colleague_id": coll_id,
                "locus_id": locus_id,
                "source": { "display_name": "Direct submission"}}

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, colleague_locus_starter, 'colleague_locus', lambda x: (x['colleague_id'], x['locus_id']))
