from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def datasetlab_starter(bud_session_maker):

    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.colleague import Colleague

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Dataset).all()])
    coll_name_institution_to_id = dict([((x.display_name, x.institution), x.id) for x in nex_session.query(Colleague).all()])
    coll_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Colleague).all()])
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
            if len(pieces) <= 14 or pieces[13] == '' or pieces[14] == '':
                continue

            coll_display_name = pieces[13].lstrip(' ').rstrip(' ')
            coll_institution = pieces[14].replace('"', '').lstrip(' ').rstrip(' ')
            data = { "source": { "display_name": 'SGD' },
                     "dataset_id": dataset_id,
                     "lab_name": pieces[13],
                     "lab_location": coll_institution }
            
            # name = pieces[13].split(' ')
            # last_name = name.pop()
            # first_name = " ".join(name)
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



