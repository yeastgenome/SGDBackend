from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def reference_unlink_starter(bud_session_maker):
    from src.sgd.model.bud.reference import RefUnlink
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    
    bud_session = bud_session_maker()

    nex_session = get_nex_session()

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])

    for bud_obj in bud_session.query(RefUnlink).all():

        locus_id = bud_id_to_locus_id.get(bud_obj.primary_key)
        if locus_id is None:
            continue
        reference_id = pmid_to_reference_id.get(bud_obj.pmid)
        if reference_id is None:
            continue
        
        yield {'reference_id': reference_id,
               'locus_id': locus_id, 
               'bud_id': bud_obj.id,
               'date_created': str(bud_obj.date_created),
               'created_by': bud_obj.created_by}

    bud_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reference_unlink_starter, 'reference_unlink', lambda x: (x['locus_id'], x['reference_id']))

