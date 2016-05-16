from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def dataset_starter(bud_session_maker):

    from src.sgd.model.nex.file import File
    from src.sgd.model.nex.obi import Obi
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.keyword import Keyword

    nex_session = get_nex_session()

    file_to_id = dict([(x.display_name, x.id) for x in nex_session.query(File).all()])
    obi_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Obi).all()]) 
    taxid_to_taxonomy_id = dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    keyword_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Keyword).all()])
    
    f = open('src/sgd/convert/data/published_datasets_metadata_A-O_201604.txt')
    for line in f:
        if line.startswith('dataset'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            if len(pieces) < 12:
                print "MISSING INFO: ", line
                continue
            format_name = pieces[0]
            display_name = pieces[1]
            source = pieces[2]
            if source == 'lab website':
                source = 'Lab website'
            if source not in ['GEO', 'ArrayExpress', 'Lab website']:
                source = 'Publication'
            assay_name = pieces[5]
            if assay_name.startswith('NTR:'):
                assay_name = assay_name.replace('NTR:', '')
            assay_id = obi_name_to_id.get(assay_name)
            if assay_id is None:
                print "The assay name:", assay_name, " is not in OBI table."
                continue
            sample_count = int(pieces[9])
            is_in_spell = int(pieces[10])
            is_in_browser = int(pieces[11])
            if sample_count is None:
                print "The sample_count column is None:", line
                continue
            if is_in_spell is None:
                print "The is_in_spell column is None:", line
                continue
            if is_in_browser is None:
                print "The is_in_browser column is None:", line
                continue
                
            data = { "source": { "display_name": source },
                     "format_name": format_name,
                     "display_name": display_name,
                     "sample_count": sample_count,
                     "assay_id": assay_id,
                     "is_in_spell": is_in_spell,
                     "is_in_browser": is_in_browser }
                     
            if pieces[3]:
                data['dbxref_id'] = pieces[3]
            if pieces[4]:
                data['dbxref_type'] = pieces[4]
                     
            if pieces[7]:
                taxonomy_id = taxid_to_taxonomy_id.get("TAX:"+pieces[7])
                if taxonomy_id is None:
                    print "The taxid: ", pieces[7], " is not in TAXONOMY table."
                else:
                    data['taxonomy_id'] = taxonomy_id

            if pieces[8]:
                data['channel_count'] = int(pieces[8])

            if pieces[12]:
                data['description'] = pieces[12].replace('"', '')
            if len(pieces) > 19:
                if pieces[18] and pieces[19]:
                    type = pieces[19]
                    if type == 'lab website':
                        type = 'Lab website'
                    data['urls'] = [{'display_name': type,
                                     'link': pieces[18],
                                     'source': { 'display_name': source },
                                     'url_type': type }]
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
    basic_convert(config.BUD_HOST, config.NEX_HOST, dataset_starter, 'dataset', lambda x: (x['display_name'], x['format_name'], x['assay_id'], x['sample_count'], x['is_in_spell'], x['is_in_browser']))



