from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def reference_deleted_starter(bud_session_maker):
    from src.sgd.model.bud.reference import RefBad
    bud_session = bud_session_maker()

    for refbad in bud_session.query(RefBad).all():
        sgdid = "" if refbad.dbxref_id is None else refbad.dbxref_id
        yield {'pmid': refbad.pubmed_id, 
               'sgdid': sgdid,
               'date_created': str(refbad.date_created),
               'created_by': refbad.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reference_deleted_starter, 'reference_deleted', lambda x: x['pmid'])

