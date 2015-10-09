from src.sgd.convert import basic_convert

__author__ = 'sweng66'

# TAXON_ID = 'NCBITaxon:559292'
TAXON_ID = 4932

def literatureannotation_starter(bud_session_maker):
    from src.sgd.model.bud.reference import LitguideFeat
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
            
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)

    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return

    for bud_obj in bud_session.query(LitguideFeat).all():
        
        litguide = bud_obj.litguide
        if litguide.topic not in ['Additional Literature', 'Omics', 'Primary Literature', 'Reviews']:
            continue

        locus_id = bud_id_to_locus_id.get(bud_obj.feature_id)
        if locus_id is None:
            print "The feature_no (bud_id) = ", bud_obj.feature_id, " is not found in Locusdbentity table."                                                       
            continue    

        reference_id = bud_id_to_reference_id.get(litguide.reference_id)
        if reference_id is None:
            print "The reference_no (bud_id) = ", litguide.reference_id, " is not found in referencedbentity table."
            continue
        
        yield { 'source': {'display_name': 'SGD'},
                'locus_id': locus_id,
                'reference_id': reference_id,
                'taxonomy_id': taxonomy_id,
                'topic': litguide.topic,
                'bud_id': bud_obj.id,
                'date_created': str(bud_obj.date_created),
                'created_by': bud_obj.created_by }

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, literatureannotation_starter, 'literatureannotation', lambda x: (x['locus_id'], x['topic'], x['reference_id']))


