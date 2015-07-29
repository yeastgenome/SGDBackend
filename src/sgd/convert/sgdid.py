from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def sgdid_starter(bud_session_maker):
    from src.sgd.model.bud.general import Dbxref, NoteFeat, DbxrefFeat, DeleteLog
    bud_session = bud_session_maker()

    print "key to note mapping..."

    key_to_note = dict([(x.primary_key, x) for x in bud_session.query(NoteFeat).filter_by(tab_name='DBXREF').all()])

    print "key to feat mapping..."

    key_to_feat = dict([(x.dbxref_id, x) for x in bud_session.query(DbxrefFeat).all()])


    print "sgd to feat mapping..."

    sgdid_to_feat = {}
    for deleteLog in bud_session.query(DeleteLog).filter_by(tab_name='FEATURE').all():
        deleteColVal = deleteLog.deleted_row.split('[:]')
        sgdid_to_feat[deleteColVal[1]] = 1 
        
    print "getting data from DBXREF..."

    for dbxref in bud_session.query(Dbxref).all():
        sgdid = dbxref.id
        if dbxref.dbxref_type.startswith('DBID '):
            sgdid = dbxref.dbxref_id
            status = dbxref.dbxref_type.replace('DBID ', '')
            note = '' if dbxref.id not in key_to_note else key_to_note[dbxref.id].note.note
            subclass = 'REFERENCE'
            if dbxref.id in key_to_feat or sgdid in sgdid_to_feat:
                subclass = 'LOCUS'
            
            print sgdid, dbxref.date_created, dbxref.created_by

            yield {'source': {'display_name': 'SGD'},
                   'display_name': sgdid,
                   'description': note,
                   'subclass': subclass,
                   'sgdid_status': status,
                   'bud_id': dbxref.id,
                   'date_created': str(dbxref.date_created),
                   'created_by': dbxref.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, sgdid_starter, 'sgdid', lambda x: x['display_name'])




