from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def datasetlab_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.colleague import Colleague

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Dataset).all()])
    coll_name_institution_to_id = dict([((x.display_name, x.institution), x.id) for x in nex_session.query(Colleague).all()])
    coll_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Colleague).all()])

    files = ['src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_dataset-OWL.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_dataset_OWL.txt',
             'src/sgd/convert/data/published_datasets_metadata_dataset-20160804.txt',
             'src/sgd/convert/data/non-GEO-dataset.tsv']

    found = {}

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip().replace('"', '')
            if line:
                pieces = line.split("\t")
                display_name = pieces[1]
                dataset_id = dataset_to_id.get(display_name)
                if dataset_id is None:
                    print "The dataset: ", display_name, " is not in DATASET table."
                    continue
                if len(pieces) <= 16 or pieces[15] == '' or pieces[16] == '':
                    continue

                coll_display_name = pieces[15].lstrip(' ').rstrip(' ')
                coll_institution = pieces[16].replace('"', '').lstrip(' ').rstrip(' ')
                if len(coll_institution) > 100:
                    coll_institution = coll_institution.replace("National Institute of Environmental Health Sciences", "NIEHS")
                    if coll_institution.startswith('Department'):
                        items = coll_institution.split(', ')
                        items.pop(0)
                        coll_institution = ', '.join(items)
                name = pieces[15].split(' ')                                                                              
                last_name = name[0]                                                                               
                first_name = name[1].replace(', ', '')
                lab_name = last_name + ' ' + first_name
                
                if (lab_name, dataset_id) in found:
                    continue
                found[(lab_name, dataset_id)] = 1
                
                data = { "source": { "display_name": 'SGD' },
                         "dataset_id": dataset_id,
                         "lab_name": lab_name,
                         "lab_location": coll_institution }
        
                colleague_id = coll_name_institution_to_id.get((coll_display_name, coll_institution))
                if colleague_id is None:
                    colleague_id = coll_name_to_id.get(coll_display_name)
                if colleague_id is not None:
                    data['colleague_id'] = colleague_id

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
    basic_convert(config.BUD_HOST, config.NEX_HOST, datasetlab_starter, 'datasetlab', lambda x: (x['lab_name'], x['lab_location'], x['dataset_id']))



