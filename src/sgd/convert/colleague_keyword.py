from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert

__author__ = 'sweng66'


def colleague_keyword_starter(bud_session_maker):
    from src.sgd.model.bud.colleague import ColleagueKeyword
    from src.sgd.model.nex.colleague import Colleague
    from src.sgd.model.nex.keyword import Keyword

    bud_session = bud_session_maker()    
    nex_session = get_nex_session()

    bud_id_to_colleague_id = dict([(x.bud_id, x.id) for x in nex_session.query(Colleague).all()])
    display_name_to_keyword_id = dict([(x.display_name, x.id) for x in nex_session.query(Keyword).all()])

    f = open('src/sgd/convert/data/category2keywordMapping.txt', 'r')
    category_to_keyword_mapping = {}
    for line in f:
        row = line.split('\t')
        if len(row) >= 2:
            category_to_keyword_mapping[row[1].strip()] = row[0]

    for bud_obj in bud_session.query(ColleagueKeyword).all():
        
        coll_id = bud_id_to_colleague_id.get(bud_obj.colleague_id)
        if coll_id is None:
            continue

        keyword = ''
        if bud_obj.keyword.keyword.startswith('RNA') or bud_obj.keyword.keyword.startswith('DNA'):
            keyword = bud_obj.keyword.keyword
        else:
            keyword = bud_obj.keyword.keyword.lower()
        if category_to_keyword_mapping.get(keyword):
            keyword = category_to_keyword_mapping[keyword]
        kw_id = display_name_to_keyword_id.get(keyword)
        if kw_id is None:
            continue

        yield {"colleague_id": coll_id,
               "keyword_id": kw_id,
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
    basic_convert(config.BUD_HOST, config.NEX_HOST, colleague_keyword_starter, 'colleague_keyword', lambda x: (x['colleague_id'], x['keyword_id']))

