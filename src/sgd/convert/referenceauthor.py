from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def referenceauthor_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference
    bud_session = bud_session_maker()
    nex_session = get_nex_session() 


    from src.sgd.model.nex.sgdid import Sgdid
    from src.sgd.model.nex.source import Source
    from src.sgd.model.nex.reference import Reference as Reference_nex
    from src.sgd.model.nex.referenceauthor import Referenceauthor

    sgdid_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Sgdid).all()])
    source_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Source).all()])
    sgdid_to_reference_id = dict([(x.sgdid, x.id) for x in nex_session.query(Reference_nex).all()])
    bud_id_to_id = dict([(x.bud_id, x.id) for x in nex_session.query(Referenceauthor).all()])
    nex_session.close()

        
    bud_refs =  bud_session.query(Reference).order_by(Reference.id.desc()).all()

    for ref_obj in bud_refs:

        if ref_obj.dbxref_id not in sgdid_to_id:
            print ref_obj.dbxref_id, " is not in SGDID table yet."
            continue

        for key in ref_obj.author_references:

            author_ref_obj = ref_obj.author_references[key]



            if author_ref_obj.id in bud_id_to_id:
                continue


            
            reference_id = sgdid_to_reference_id.get(ref_obj.dbxref_id)

            if reference_id is None:
                continue

            source = 'SGD'
            if ref_obj.pubmed_id is not None:
                source = 'NCBI'
            elif 'PDB' in ref_obj.source:
                source = 'PDB'
            elif 'YPD' in ref_obj.source:
                source = 'YPD'

            source_id = source_to_id.get(source)
            if source_id is None:
                print source, "is not in SOURCE table."
                continue

            yield {'display_name': author_ref_obj.author_name,
                   'source_id': source_id,
                   'author_order': author_ref_obj.order,
                   'author_type': author_ref_obj.type,
                   'reference_id': reference_id, 
                   'bud_id': author_ref_obj.id,
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
    basic_convert(config.BUD_HOST, config.NEX_HOST, referenceauthor_starter, 'referenceauthor', lambda x: (x['display_name'], x['author_order'], x['author_type']))

