from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def reference_file_starter(bud_session_maker):

    from src.sgd.model.nex.file import File
    from src.sgd.model.nex.reference import Reference

    nex_session = get_nex_session()

    file_to_id = dict([(x.display_name, x.id) for x in nex_session.query(File).all()])
    pmid_to_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    
    # f = open('src/sgd/convert/data/published_datasets-files_metadata_A-O_201604.txt')
    files = ['src/sgd/convert/data/published_datasets_metadata_file-20160804.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_file.tsv_round2fix_fixdupRM_fixRMdescriptionEDWs_owl.tsv',
             'src/sgd/convert/data/non-GEO-file.tsv']

    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('bun_filepath'):
                continue
            line = line.strip()
            if line:
                pieces = line.split("\t")
                display_name = pieces[3]
                file_id = file_to_id.get(display_name)
                if file_id is None:
                    print "The file: ", display_name, " is not in FILEDBENTITY table."
                    continue
                pmids = pieces[18].split("|")
                for pmid in pmids:
                    if pmid == '':
                        continue
                    reference_id = pmid_to_id.get(int(pmid))
                    if reference_id is None:
                        print "The pmid: ", pmid, " is not in the REFERENCEDBENTITY table."
                        continue
                    yield { "source": { "display_name": 'SGD' },
                            "reference_id": reference_id,
                            "file_id": file_id }

    f.close()



def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, reference_file_starter, 'reference_file', lambda x: (x['reference_id'], x['file_id']))



