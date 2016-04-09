from src.sgd.convert import basic_convert

__author__ = 'sweng66'

SRC = 'SGD'

def curation_starter(bud_session_maker):

    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.bud.reference import RefCuration
    from src.sgd.model.bud.feature import FeatCuration

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    
    for x in bud_session.query(FeatCuration).all():
        dbentity_id = bud_id_to_locus_id.get(x.feature_id)
        if dbentity_id is None:
            print "The feature_no: ", x.feature_id, " is not in LOCUSDBENTITY table."
            continue
        data = { "source": { 'display_name': SRC },
                 "subclass": 'LOCUS',
                 "dbentity_id": dbentity_id,
                 "curation_task": x.task,
                 "date_created": str(x.date_created),
                 "created_by": x.created_by }

        if x.comment is not None:
            data['curator_comment'] = x.comment
        yield data

    for x in bud_session.query(RefCuration).all():
        dbentity_id = bud_id_to_reference_id.get(x.reference_id)
        if dbentity_id is None:
            print "The reference_no: ", x.reference_id, " is not in REFERENCEDBENTITY table."
            continue

        data = { "source": { 'display_name': SRC },
                 "subclass": 'REFERENCE',
                 "dbentity_id": dbentity_id,
                 "curation_task": x.task,
                 "date_created": str(x.date_created),
                 "created_by": x.created_by }

        if x.comment is not None:
            data['curator_comment'] = x.comment
        locus_id = bud_id_to_locus_id.get(x.feature_id)
        if locus_id is not None:
            data['locus_id'] = locus_id
        yield data


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, curation_starter, 'curation', lambda x: (x['dbentity_id'], x['subclass'], x['curation_task'], x.get('locus_id')))



