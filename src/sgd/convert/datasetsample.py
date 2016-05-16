from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def datasetsample_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.obi import Obi

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Dataset).all()])
    obi_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Obi).all()])

    ## for some reason, can't access source_id from dataset table - weird so have to
    ## open this file to get the source.. =(
    f = open('src/sgd/convert/data/published_datasets_metadata_A-O_201604.txt')
    dataset_to_src = {}
    for line in f:
        if line.startswith('dataset'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            source = pieces[2]
            if source == 'lab website':
                source = 'Lab website'
            if source not in ['GEO', 'ArrayExpress', 'Lab website']:
                source = 'Publication'
            dataset_to_src[pieces[0]] = source

    f.close()

    f = open('src/sgd/convert/data/published_datasets-samples_metadata_A-O_201604.txt')
    
    for line in f:
        if line.startswith('dataset'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            format_name = pieces[0]
            dataset_id = dataset_to_id.get(format_name)
            if dataset_id is None:
                print "The dataset: ", format_name, " is not in DATASET table."
                continue

            if len(pieces) <= 8 or pieces[8] == '':
                continue
            source = dataset_to_src[format_name]
            if source is None:
                print "No source available for dataset: ", format_name
                continue

            data = { "source": { "display_name": source },
                     "dataset_id": dataset_id,
                     "display_name": pieces[1],
                     "format_name": pieces[1].replace(' ', '_') + '_' + pieces[8],
                     "sample_order": int(pieces[8])}
            if pieces[2] != '':
                data['description'] = pieces[2]
            if pieces[3] != '':
                data['dbxref_id'] = pieces[3]
            if pieces[4] != '':
                data['dbxref_type'] = pieces[4]
            if pieces[5] != '':
                data['biosample'] = pieces[5]
            if pieces[7] != '':
                data['strain_name'] = pieces[7]

            yield data

    f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, datasetsample_starter, 'datasetsample', lambda x: (x['format_name'], x['display_name'], x['sample_order'], x['dataset_id']))


