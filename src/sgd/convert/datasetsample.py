from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def datasetsample_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.obi import Obi
    from src.sgd.model.nex.taxonomy import Taxonomy

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Dataset).all()])
    obi_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Obi).all()])
    taxid_to_taxonomy_id = dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])

    ## for some reason, can't access source_id from dataset table - weird so have to
    ## open this file to get the source.. =(
    files = ['src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_dataset-OWL.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_dataset_OWL.txt',
             'src/sgd/convert/data/published_datasets_metadata_dataset-20160804.txt',
             'src/sgd/convert/data/non-GEO-dataset.tsv']

    dataset_to_src = {}
    for file in files:
        f = open(file)
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

    files = ['src/sgd/convert/data/published_datasets_metadata_sample-20160804.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_datasetsample-OWL.txt_round2fix.tsv_wtaxons.tsv',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_datasetsample-OWL.txt_round2fix.tsv_wtaxons_cleaned.txt',
             'src/sgd/convert/data/non-GEO-datasetsample_OWL.txt']

    format_name2display_name = {}
    dataset2index = {}
    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip()
            if line:
                pieces = line.replace('"', '').split("\t")
                dataset_format_name = pieces[0]
                dataset_id = dataset_to_id.get(dataset_format_name)
                if dataset_id is None:
                    print "The dataset: ", dataset_format_name, " is not in DATASET table."
                    continue

                if len(pieces) <= 9 or pieces[8] == '':
                    continue
                source = dataset_to_src[dataset_format_name]
                if source is None:
                    print "No source available for dataset: ", dataset_format_name
                    continue

                display_name = pieces[1]
                # format_name = pieces[1].replace(' ', '_') + '_' + pieces[8]
                data = { "source": { "display_name": source },
                         "dataset_id": dataset_id,
                         "display_name": display_name,
                         "sample_order": int(pieces[8])}
                if pieces[2] != '':
                    data['description'] = pieces[2]
                    if len(pieces[2]) > 500:
                        data['description'] = display_name
                if pieces[5] != '':
                    data['biosample'] = pieces[5]
                if pieces[7] != '':
                    data['strain_name'] = pieces[7]
                if pieces[9]:
                    taxonomy_id = taxid_to_taxonomy_id.get("TAX:"+pieces[9])
                    if taxonomy_id is None:
                        print "The taxid: ", pieces[9], " is not in TAXONOMY table."
                    else:
                        data['taxonomy_id'] = taxonomy_id

                if pieces[3] == '':
                    index = dataset2index.get(dataset_format_name, 0) + 1
                    data['format_name'] = dataset_format_name + "_sample_" + str(index)
                    dataset2index[dataset_format_name] = index
                    data['link'] = "/datasetsample/" + data['format_name']
                    yield data
                else:
                    ids = pieces[3].replace(" ", "").split(",")
                    data['dbxref_type'] = pieces[4]
                    for id in ids:
                        if format_name2display_name.get(id):
                            print "The format_name: ", id, " has been used for other sample", format_name2display_name.get(id)
                            continue
                        format_name2display_name[id] = display_name
                        data['format_name'] = dataset_format_name + "_" + id
                        data['link'] = "/datasetsample/" + data['format_name']
                        data['dbxref_id'] = id
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
    basic_convert(config.BUD_HOST, config.NEX_HOST, datasetsample_starter, 'datasetsample', lambda x: (x['format_name'], x['display_name'], x['sample_order'], x['dataset_id'], x.get('dbxref_id')))


