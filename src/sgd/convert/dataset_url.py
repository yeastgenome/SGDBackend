from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def dataset_url_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    
    nex_session = get_nex_session()

    dataset_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Dataset).all()])

    files = ['src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_dataset-OWL.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_dataset_OWL.txt',
             'src/sgd/convert/data/published_datasets_metadata_dataset-20160804.txt',
             'src/sgd/convert/data/non-GEO-dataset.tsv']

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip().replace('"', '')
            if line:
                pieces = line.split("\t")
                display_name = pieces[1]
                source = pieces[2]
                if source == 'lab website':
                    source = 'Lab website'
                if source not in ['GEO', 'ArrayExpress', 'Lab website']:
                    source = 'Publication'
                dataset_id = dataset_to_id.get(display_name)
                if dataset_id is None:
                    print "The dataset: ", display_name, " is not in DATASET table."
                    continue
                if len(pieces) <= 21 or pieces[21] == '':
                    continue
                urls = pieces[20].replace(' | ', '|').split('|')
                types = pieces[21].replace(' | ', '|').split('|')

                i = 0
                for url in urls:
                    if url == '':
                        continue
                    if len(types) > i:
                        type = types[i]
                        i = i + 1
                        if type == 'lab website': 
                            type = 'Lab website'
                        if type == 'Website':
                            type == 'Archive website'
                        yield { 'display_name': type,
                                'dataset_id': dataset_id,
                                'link': url,
                                'source': { 'display_name': source },
                                'url_type': type }

        f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dataset_url_starter, 'dataset_url', lambda x: (x['link'], x['url_type'], x['display_name'], x['dataset_id']))



