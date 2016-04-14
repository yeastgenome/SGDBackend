from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

source = 'SGD'
TAXON_ID = "TAX:4932"

def proteinexptannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    
    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    name_to_locus_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    
    f = open('src/sgd/convert/data/proteinexptannotation.txt', 'r')

    for line in f:
        pieces = line.strip().split('\t')
        locus_id = name_to_locus_id.get(pieces[0])
        if locus_id is None:
            print "The name: ", pieces[0], " is not in LOCUSDBENTITY table."
            continue
        reference_id = pmid_to_reference_id.get(int(pieces[2]))
        if reference_id is None:
            print "The PMID: ", pieces[2], " is not in REFERENCEDBENTITY table."
            continue
        experiment_type = None
        if "abundance" in pieces[3]:
            experiment_type = "abundance"
        elif "localization" in pieces[3]:
            experiment_type = "localization"
        else:
            print "Unknown experiment type: ", pieces[3]
            continue

        yield { "source": { "display_name": source },
                "locus_id": locus_id,
                "taxonomy_id": taxonomy_id,
                "reference_id": reference_id,
                "experiment_type": experiment_type,
                "data_value": pieces[4],
                "data_unit": pieces[5],
                "date_created": pieces[6],
                "created_by": pieces[7] }

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()
   
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, proteinexptannotation_starter, 'proteinexptannotation', lambda x: (x['locus_id'], x['taxonomy_id'], x['reference_id'], x['experiment_type'], x['data_value'], x['data_unit']))
