from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_sgdid_to_reference_id

__author__ = 'sweng66'

def reference_author_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference
    bud_session = bud_session_maker()

    for ref_obj in bud_session.query(Reference).order_by(Reference.id.desc()).all():

        ## only load old references (before 7/28/2015) - new sgdids are not in sgdid table yet so skip them for now
        if int(ref_obj.id) >= 99472:
            continue

        for key in ref_obj.author_references:

            author_ref_obj = ref_obj.author_references[key]
            
            reference_id = get_sgdid_to_reference_id(ref_obj.dbxref_id)

            source = 'SGD'
            if ref_obj.pubmed_id is not None:
                source = 'NCBI'
            elif 'PDB' in ref_obj.source:
                source = 'PDB'
            elif 'YPD' in ref_obj.source:
                source = 'YPD'

            yield {'display_name': author_ref_obj.author_name,
                   'source': {'display_name': source},
                   'author_order': author_ref_obj.order,
                   'author_type': author_ref_obj.type,
                   'reference_id': reference_id, 
                   'bud_id': author_ref_obj.id,
                   'date_created': str(ref_obj.date_created),
                   'created_by': ref_obj.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reference_author_starter, 'reference_author', lambda x: (x['display_name'], x['author_order'], x['author_type']))

