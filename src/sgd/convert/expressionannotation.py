from src.sgd.convert import basic_convert

__author__ = 'sweng66'

TAXON = "TAX:4932"

def expressionannotation_starter(bud_session_maker):

    from src.sgd.model.nex.datasetsample import Datasetsample
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.expressionannotation import Expressionannotation

    nex_session = get_nex_session()

    expressionannot_to_id = dict([((x.dbentity_id, x.reference_id, x.datasetsample_id), x.id) for x in nex_session.query(Expressionannotation).all()])
    datasetsample_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Datasetsample).all()])
    pmid_to_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    feature_name_to_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    taxonomy_obj = nex_session.query(Taxonomy).filter_by(taxid=TAXON).first()
    taxonomy_id = taxonomy_obj.id
    

    files = ['src/sgd/convert/data/expression_annotation.txt']

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('DATASETSAMPLE'):
                continue
            line = line.strip()
            if line:
                pieces = line.strip().split("\t")
                
                if pieces[2] == 'NA':
                    continue
                reference_id = pmid_to_id.get(int(pieces[1]))
                if reference_id is None:
                    print "The PMID: ", pieces[1], " is not in the database"
                    continue

                datasetsample_id = datasetsample_to_id.get(pieces[0])
                if datasetsample_id is None:
                    print "The datasetsample: ", pieces[0], " is not in the database."
                    continue

                dbentity_id = feature_name_to_id.get(pieces[3])
                if dbentity_id is None:
                    print "The feature_name: ", pieces[3], " is not in the database."
                    continue
                
                key = (dbentity_id, reference_id, datasetsample_id)
                if key in expressionannot_to_id:
                    continue

                yield { "source": { "display_name": "SGD" },
                        "dbentity_id": dbentity_id,
                        "reference_id": reference_id,
                        "taxonomy_id": taxonomy_id,
                        "datasetsample_id": datasetsample_id,
                        "expression_value": float(pieces[2]) }
                        
        f.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, expressionannotation_starter, 'expressionannotation', lambda x: (x['dbentity_id'], x['taxonomy_id'], x['reference_id'], x['datasetsample_id'], x['expression_value']))



