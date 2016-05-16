from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def filepath_starter(bud_session_maker):

    from src.sgd.model.nex.filepath import Filepath

    nex_session = get_nex_session()
    path_to_id = dict([(x.filepath, x.id) for x in nex_session.query(Filepath).all()])
    
    f = open('src/sgd/convert/data/published_datasets-files_metadata_A-O_201604.txt')

    found = {}
    for line in f:
        if line.startswith('bun_filepath'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            filepath = pieces[1]
            if filepath is None:
                continue
            if filepath in found or path_to_id.get(filepath):
                continue
            found[filepath] = 1

            yield { 'source': { 'display_name': 'SGD'},
                    'filepath': filepath }
 
    f.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, filepath_starter, 'filepath', lambda x: x['filepath'])


