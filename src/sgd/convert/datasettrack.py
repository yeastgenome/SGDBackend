from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def datasettrack(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.colleague import Colleague

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Dataset).all()])
    
    ## in case we have more files late
    files = ['src/sgd/convert/data/published_datasets_metadata_track-20160804.txt']

    found = {}

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip().replace('"', '')
            if line:
                pieces = line.strip().split("\t")
                dataset_format_name = pieces[0]
                display_name = pieces[1]
                format_name = pieces[2]
                track_order = int(pieces[3])
                dataset_id = dataset_to_id.get(dataset_format_name)
                if dataset_id is None:
                    print "The dataset: ", dataset_format_name, " is not in DATASET table."
                    continue

                yield { "dataset_id": dataset_id,
                        "source": { "display_name": 'SGD' },
                        "format_name": format_name,
                        "display_name": display_name,
                        "track_order": track_order,
                        "track_status": 'Active' }

        f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, datasettrack, 'datasettrack', lambda x: (x['format_name'], x['display_name'], x['track_order'], x['track_status'], x['dataset_id']))



