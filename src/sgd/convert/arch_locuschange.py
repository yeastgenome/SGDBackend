from src.sgd.convert import basic_convert

__author__ = 'sweng66'

SRC = 'SGD'

def arch_locuschange_starter(bud_session_maker):

    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.bud.feature import Archive

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    bud_id_to_dbentity_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    
    for x in bud_session.query(Archive).all():
        dbentity_id = bud_id_to_dbentity_id.get(x.feature_id)
        if dbentity_id is None:
            print "The feature_no: ", x.feature_id, " is not in LOCUSDBENTITY table."
            continue
        old_value = "" if x.old_value is None else x.old_value
        new_value = "" if x.new_value is None else x.new_value
        change_type = ""
        if x.archive_type == 'Feature qualifier':
            change_type = 'Qualifier'
        elif x.archive_type == 'Feature status':
            change_type = 'Status'
        else:
            change_type = x.archive_type

        yield { "source": { 'display_name': SRC },
                "dbentity_id": dbentity_id,
                "change_type": change_type, 
                "bud_id": x.id,
                "old_value": old_value,
                "new_value": new_value,
                "date_changed": str(x.date_created),
                "changed_by": x.created_by,
                "date_archived": str(x.date_created) }

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, arch_locuschange_starter, 'arch_locuschange', lambda x: (x['dbentity_id'], x['change_type'], x['date_changed'], x['changed_by'], x['date_archived']))



