from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def referencedeleted_starter(bud_session_maker):
    from src.sgd.model.bud.reference import RefBad
    from src.sgd.model.bud.general import Dbxref, NoteFeat
    from src.sgd.model.nex.sgdid import Sgdid
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.referencedeleted import Referencedeleted

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    dbxref_id_to_sgdid = dict([(x.id, x.dbxref_id) for x in bud_session.query(Dbxref).filter_by(dbxref_type='DBID Deleted').all()])
    sgdid_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Sgdid).all()])
    pmid_to_refdel_id = dict([(x.pmid, x.id) for x in nex_session.query(Referencedeleted).all()])
    pmid_to_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    nex_session.close()

    sgdid_to_note = {}
    for x in bud_session.query(NoteFeat).filter_by(tab_name='DBXREF').all():
        sgdid = dbxref_id_to_sgdid.get(x.primary_key)
        if sgdid is None:
            continue
        sgdid_to_note[sgdid] = x.note.note

    for refbad in bud_session.query(RefBad).all():

        sgdid = "" if refbad.dbxref_id is None else refbad.dbxref_id
        note = ""
        if sgdid != "":
            if sgdid_to_note.get(sgdid) is not None:
                note = sgdid_to_note.get(sgdid)
            if sgdid_to_id.get(sgdid) is None:
                continue
        pmid = refbad.pubmed_id
        if pmid_to_id.get(pmid) is not None:
            continue
        if pmid in pmid_to_refdel_id:
            continue
        pmid_to_refdel_id[pmid] = 1

        data = { 'pmid': pmid,
                 'reason_deleted': note,
                 'date_created': str(refbad.date_created),
                 'created_by': refbad.created_by }

        if sgdid != "":
            data['sgdid'] = sgdid

        yield data

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, referencedeleted_starter, 'referencedeleted', lambda x: x['pmid'])

