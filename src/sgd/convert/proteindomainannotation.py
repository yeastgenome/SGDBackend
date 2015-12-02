from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id
from src.sgd.convert.gpad_config import curator_id, computational_created_by,  \
    go_db_code_mapping, go_ref_mapping, current_go_qualifier, email_receiver, \
    email_subject

__author__ = 'sweng66'

TAXON_ID = "TAX:4932"

def proteindomainannotation_starter(bud_session_maker):

    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.proteindomain import Proteindomain

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return

    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    display_name_to_proteindomain_id = dict([(x.display_name, x.id) for x in nex_session.query(Proteindomain).all()])
    name_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])

    source = 'InterPro'

    f = open('src/sgd/convert/data/domains.tab', 'r')
    for line in f:
        row = line.strip().split('\t')
        dbentity_id = name_to_dbentity_id.get(row[0])
        if dbentity_id is None:
            print "The feature name=", row[0], " is not in LOCUSDBENTITY table."
            continue
        proteindomain_id = display_name_to_proteindomain_id.get(row[4].strip())
        if proteindomain_id is None:
            print "The domain name=", row[4], " is not in PROTEINDOMAIN table."
            continue
        if row[9] != 'T':
            continue

        date = row[10].split('-')
        date_of_run = date[2] + '-' + date[0] + '-' + date[1]
        yield { "source": { "display_name": source},
                "dbentity_id": dbentity_id,
                "taxonomy_id": taxonomy_id,
                "proteindomain_id": proteindomain_id,
                "start_index": int(row[6]),
                "end_index": int(row[7]),
                "date_of_run": date_of_run}


    bud_session.close()

   
def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, proteindomainannotation_starter, 'proteindomainannotation', lambda x: (x['dbentity_id'], x['proteindomain_id'], x['start_index'], x['end_index']))


