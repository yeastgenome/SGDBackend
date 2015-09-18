from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def colleague_url_starter(bud_session_maker):
    from src.sgd.model.bud.colleague import ColleagueUrl
    from src.sgd.model.nex.colleague import Colleague
    
    bud_session = bud_session_maker()    
    nex_session = get_nex_session()

    bud_id_to_colleague_id = dict([(x.bud_id, x.id) for x in nex_session.query(Colleague).all()])
    
    for bud_obj in bud_session.query(ColleagueUrl).all():
        
        coll_id = bud_id_to_colleague_id.get(bud_obj.colleague_id)
        if coll_id is None:
            continue
        if bud_obj.url.url_type.startswith('Reference'):
            continue

        yield { "colleague_id": coll_id,
                "display_name": bud_obj.url.url,
                "url_type": bud_obj.url.url_type,
                "bud_id": bud_obj.url.id,
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
    basic_convert(config.BUD_HOST, config.NEX_HOST, colleague_url_starter, 'colleague_url', lambda x: (x['colleague_id'], x['display_name'], x['url_type']))
