from src.sgd.convert import basic_convert
from src.sgd.convert.util import is_number

__author__ = 'sweng66'

TAXON_ID = 4932

def goslimannotation_starter(bud_session_maker):

    from src.sgd.model.nex.go import Go
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.goslim import Goslim
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.reference import Reference

    nex_session = get_nex_session()

    goid_to_go_id = dict([(x.goid, x.id) for x in nex_session.query(Go).all()])
    sgdid_to_dbentity_id = dict([(x.sgdid, x.id) for x in nex_session.query(Locus).all()])
    go_id_to_goslim_id = dict([(x.go_id, x.id) for x in nex_session.query(Goslim).all()])
    goslim_id_to_slim_name = dict([(x.id, x.slim_name) for x in nex_session.query(Goslim).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    
    f = open("src/sgd/convert/data/go_slim_mapping.tab")
    for line in f:
        pieces = line.split('\t')
        if len(pieces) >= 6:
            goid = pieces[5]
            sgdid = pieces[2]
            go_id = goid_to_go_id.get(goid)
            if go_id is None:
                print "The goid ", goid, " is not in GO table."
                continue
            goslim_id = go_id_to_goslim_id.get(go_id)
            if goslim_id is None:
                print "The go_id", go_id, " is not in GOSLIM table."
                continue
            dbentity_id = sgdid_to_dbentity_id.get(sgdid)
            if dbentity_id is None:
                print "The sgdid ", sgdid, " is not in LOCUSDBENTITY table."
                continue

            slim_name = goslim_id_to_slim_name.get(goslim_id)
            source = 'SGD'
            if slim_name.startswith('Generic'):
                slim_name = 'GOC'

            yield {'source': { "display_name": source },
                   'dbentity_id': dbentity_id,
                   'taxonomy_id': taxonomy_id,
                   'goslim_id': goslim_id }

    nex_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()
                    
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, goslimannotation_starter, 'goslimannotation', lambda x: (x['dbentity_id'], x['goslim_id'], x.get('reference_id')))





