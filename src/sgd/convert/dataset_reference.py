from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def dataset_reference_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.reference import Reference

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Dataset).all()])
    pmid_to_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    
    f = open('src/sgd/convert/data/published_datasets_metadata_A-O_201604.txt')
    
    for line in f:
        if line.startswith('dataset'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            display_name = pieces[1]
            dataset_id = dataset_to_id.get(display_name)
            if dataset_id is None:
                print "The dataset: ", display_name, " is not in DATASET table."
                continue
            if len(pieces) <= 16 or pieces[16] == '':
                continue
            pmids = pieces[16].split('|')
            for pmid in pmids:
                reference_id = pmid_to_id.get(int(pmid))
                if reference_id is None:
                    print "The PMID: ", pmid, " is not in REFERENCEDBENTITY table."
                    continue
                yield { "source": { "display_name": 'SGD' },
                        "reference_id": reference_id,
                        "dataset_id": dataset_id }

    f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dataset_reference_starter, 'dataset_reference', lambda x: (x['reference_id'], x['dataset_id']))



