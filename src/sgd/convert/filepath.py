from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def filepath_starter(bud_session_maker):

    from src.sgd.model.nex.filepath import Filepath

    nex_session = get_nex_session()
    path_to_id = dict([(x.filepath, x.id) for x in nex_session.query(Filepath).all()])
    
    found = {}

    files = ['src/sgd/convert/data/published_datasets_metadata_file-20160804.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_file.tsv_round2fix_fixdupRM_fixRMdescriptionEDWs_owl.tsv',
             'src/sgd/convert/data/non-GEO-file.tsv']

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('bun_filepath') or line.startswith('bun filepath'):
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


