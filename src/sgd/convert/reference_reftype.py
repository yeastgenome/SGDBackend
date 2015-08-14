from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_sgdid_to_reference_id

__author__ = 'sweng66'

def reference_reftype_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference
    bud_session = bud_session_maker()

    for ref_obj in bud_session.query(Reference).order_by(Reference.id.desc()).all():

        ## only load old references (before 7/28/2015) - new sgdids are not in sgdid table yet so skip them for now
        if int(ref_obj.id) >= 99472:
            continue

        for key in ref_obj.reftype_references:

            refreftype_obj = ref_obj.reftype_references[key]
            
            reference_id = get_sgdid_to_reference_id(ref_obj.dbxref_id)

            print "reference_id=", reference_id

            yield {'display_name': refreftype_obj.reftype_name,
                   'source': {'display_name': refreftype_obj.reftype_source},
                   'reference_id': reference_id, 
                   'bud_id': refreftype_obj.id,
                   'date_created': str(ref_obj.date_created),
                   'created_by': ref_obj.created_by}

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reference_reftype_starter, 'reference_reftype', lambda x: (x['display_name'], x['reference_id']))

