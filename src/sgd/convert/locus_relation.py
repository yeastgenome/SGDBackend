from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'sweng66'

def locus_relation_starter(bud_session_maker):
    from src.sgd.model.bud.feature import FeatRel
    from src.sgd.model.nex.locus import Locus
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    bud_id_to_dbentity_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])

    for bud_obj in bud_session.query(FeatRel).all():
        if bud_obj.relationship_type == 'pair' or bud_obj.relationship_type is None:
            continue

        if bud_obj.parent_id not in bud_id_to_dbentity_id or bud_obj.child_id not in bud_id_to_dbentity_id:
            continue

        bud_id = bud_obj.id
        parent_id = bud_id_to_dbentity_id[bud_obj.parent_id]
        child_id = bud_id_to_dbentity_id[bud_obj.child_id]
        source = bud_obj.parent.source
        print "parent_id: ", parent_id             
        print "child_id:", child_id
        print "source:", source
        print "bud_id:", bud_id   

        yield({
            "parent_id": parent_id,
            "child_id": child_id,
            "source": { "display_name": source},
            "bud_id": bud_id,
            "ro_id": get_relation_to_ro_id(bud_obj.relationship_type.replace('_', ' ')),
            "date_created": str(bud_obj.date_created),
            "created_by": bud_obj.created_by
            })
    
    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, locus_relation_starter, 'locus_relation', lambda x: (x['parent_id'], x['child_id'], x['ro_id']))
