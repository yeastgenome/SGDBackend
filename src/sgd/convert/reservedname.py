from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def reservedname_starter(bud_session_maker):
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.colleague import Colleague
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    bud_id_to_colleague_id = dict([(x.bud_id, x.id) for x in nex_session.query(Colleague).all()])

    from src.sgd.model.bud.reference import Reflink

    feature_no_to_reference_id = {}
    for x in bud_session.query(Reflink).filter_by(tab_name='GENE_RESERVATION').all():
        feature_no = x.primary_key
        ref_bud_id = x.reference_id
        reference_id = bud_id_to_reference_id.get(ref_bud_id)
        if reference_id is None:
            print "The reference bud_id: ", ref_bud_id, " is not in the Reference table."
            continue
        feature_no_to_reference_id[feature_no] = reference_id

    from src.sgd.model.bud.general import NoteFeat
    
    feature_no_to_note = {}
    for x in bud_session.query(NoteFeat).filter_by(tab_name='FEATURE').all():
        if x.note.note_type == 'Reserved Name Note':
            feature_no_to_note[x.primary_key] = x.note.note

    from src.sgd.model.bud.colleague import CollGeneres

    for x in bud_session.query(CollGeneres).all():

        colleague_id = bud_id_to_colleague_id.get(x.colleague_id)
        if colleague_id is None:
            print "The colleague_no=", x.colleague_id, " is not in Colleague table."
            continue
        
        y = x.genereservation
        if y.date_standardized is not None or y.reserved_gene_name is None:
            continue
    
        locus_id = bud_id_to_locus_id.get(x.feature_id) 
        if locus_id is None:
            print "The feature_no = ", x.feature_id, " is not in the LOCUSENTITY table."
            # continue
        display_name = y.reserved_gene_name
        format_name = display_name
        data = { "display_name": display_name,
                 "format_name": format_name,
                 "link": "/reservedname/" + format_name,
                 "source": { "display_name": 'Direct Submission' },
                 "bud_id": x.id,
                 "colleague_id": colleague_id,
                 "reservation_date": str(y.reservation_date),
                 "expiration_date": str(y.expiration_date),
                 "date_created": str(y.date_created),
                 "created_by": str(y.created_by) }

        if locus_id is not None:
            data['locus_id'] = locus_id

        reference_id = feature_no_to_reference_id.get(x.feature_id)
        if reference_id is not None:
            data['reference_id'] = reference_id

        note = feature_no_to_note.get(x.feature_id)
        if note is not None:
            data['description'] = note

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
    basic_convert(config.BUD_HOST, config.NEX_HOST, reservedname_starter, 'reservedname', lambda x: (x['display_name'], x.get('locus_id'), x['colleague_id']))

