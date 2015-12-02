from src.sgd.convert import basic_convert

__author__ = 'sweng66'

TAXON_ID = "TAX:4932"

def enzymeannotation_starter(bud_session_maker):
    from src.sgd.model.bud.general import Dbxref, DbxrefFeat
    from src.sgd.model.bud.reference import Reflink
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.ec import Ec

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    ecid_to_ec_id = dict([(x.ecid, x.id) for x in nex_session.query(Ec).all()])
    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    # bud_id_to_ec_number = dict([(x.id, x.dbxref_id) for x in bud_session.query(Dbxref).filter_by(dbxref_type='EC number').all()])
    ref_bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])

    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)

    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return

    dbxref_feat_bud_id_to_reference_id = {}
    for x in bud_session.query(Reflink).filter_by(tab_name='DBXREF_FEAT'):
        reference_id = ref_bud_id_to_reference_id.get(x.reference_id)
        if reference_id is not None:
            dbxref_feat_bud_id_to_reference_id[x.primary_key] = reference_id

#    for x in bud_session.query(DbxrefFeat).join(DbxrefFeat.dbxref).filter_by(Dbxref.dbxref_type=='EC number').all(): ## for some reason this doesn't work

    for x in bud_session.query(DbxrefFeat).join(DbxrefFeat.dbxref).all():

        if x.dbxref.dbxref_type != 'EC number':
            continue

        locus_id = bud_id_to_locus_id.get(x.feature_id)
        if locus_id is None:
            print "The feature_no (bud_id) = ", bud_obj.feature_id, " is not found in Locusdbentity table."                       
            continue    
        
        dbxref = x.dbxref
        ec_id = ecid_to_ec_id.get("EC:" + dbxref.dbxref_id)
        if ec_id is None:
            print "The ec_number = ", dbxref.dbxref_id, " is not found in EC table."
            continue
        
        reference_id = dbxref_feat_bud_id_to_reference_id.get(x.id)
        if reference_id is None:
            print "The reference for the dbxref_feat entry with dbxref_feat_no = ", x.id, " is not found in referencedbentity table."
            continue
        
        # print locus_id, reference_id, ec_id 
        
        yield { 'source': {'display_name': 'SGD'},
                'dbentity_id': locus_id,
                'reference_id': reference_id,
                'taxonomy_id': taxonomy_id,
                'ec_id': ec_id,
                'bud_id': x.id,
                'date_created': str(dbxref.date_created),
                'created_by': dbxref.created_by }

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, enzymeannotation_starter, 'enzymeannotation', lambda x: (x['dbentity_id'], x['ec_id'], x['reference_id']))


