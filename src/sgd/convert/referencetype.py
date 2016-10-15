from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def referencetype_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference
    bud_session = bud_session_maker()
    nex_session = get_nex_session() 

    from src.sgd.model.nex.sgdid import Sgdid
    from src.sgd.model.nex.source import Source
    from src.sgd.model.nex.reference import Reference as Reference_nex
    from src.sgd.model.nex.referencetype import Referencetype

    sgdid_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Sgdid).all()])
    source_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Source).all()])
    bud_id_to_id =  dict([(x.bud_id, x.id) for x in nex_session.query(Referencetype).all()])
    sgdid_to_reference_id = dict([(x.sgdid, x.id) for x in nex_session.query(Reference_nex).all()])
    nex_session.close()

    for ref_obj in bud_session.query(Reference).order_by(Reference.id.desc()).all():

        if ref_obj.dbxref_id not in sgdid_to_id:
            print ref_obj.dbxref_id, " is not in SGDID table yet."
            continue


        for key in ref_obj.reftype_references:

            refreftype_obj = ref_obj.reftype_references[key]

            if refreftype_obj.id in bud_id_to_id:
                continue

            reference_id = sgdid_to_reference_id.get(ref_obj.dbxref_id)
            if reference_id is None:
                print ref_obj.dbxref_id, " is not in the REFERENCE Table."
                continue
            
            source_id = source_to_id.get(refreftype_obj.reftype_source)
            if source_id is None:
                print refreftype_obj.reftype_source, " is not in SOURCE Table."
                continue

            yield {'display_name': refreftype_obj.reftype_name,
                   'source_id': source_id,
                   'reference_id': reference_id, 
                   'bud_id': refreftype_obj.id,
                   'date_created': str(ref_obj.date_created),
                   'created_by': ref_obj.created_by}

    bud_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, referencetype_starter, 'referencetype', lambda x: (x['display_name'], x['reference_id']))

