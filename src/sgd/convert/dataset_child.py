from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def dataset_starter(bud_session_maker):
    
    from src.sgd.model.nex.dataset import Dataset
    from src.sgd.model.nex.file import File
    from src.sgd.model.nex.obi import Obi
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.keyword import Keyword

    nex_session = get_nex_session()

    dataset_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Dataset).all()])
    file_to_id = dict([(x.display_name, x.id) for x in nex_session.query(File).all()])
    obi_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Obi).all()]) 
    taxid_to_taxonomy_id = dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    keyword_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Keyword).all()])

    ## have to load the NOTinSPELL before published ones - since some rows are in both 
    ## but NOTinSPELL dataset contains the complete info - except URL, PMIDs & strains 
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
                if len(pieces) < 12:
                    print "MISSING INFO: ", line
                    continue

                ## there is no parent so skip (already loaded)
                if pieces[6] == '':
                    continue
                
                parent_dataset_id = dataset_to_id.get(pieces[6])
                   
                format_name = pieces[0]

                if format_name in found:
                    continue
                found[format_name] = 1

                display_name = pieces[1]
                source = pieces[2]
                if source == 'lab website':
                    source = 'Lab website'
                if source not in ['GEO', 'ArrayExpress', 'Lab website']:
                    source = 'Publication'
                assay_name = pieces[7]
                if assay_name == 'OBI:0000626':
                    assay_name = 'DNA sequencing'
                if assay_name == 'transcriptional profiling by array assay':
                    assay_name = 'transcription profiling by array assay'
                if assay_name.startswith('NTR:'):
                    assay_name = assay_name.replace('NTR:', '')
                assay_id = obi_name_to_id.get(assay_name)
                if assay_id is None:
                    print "The assay name:", assay_name, " is not in OBI table."
                    continue
                
                if pieces[11] == '' or pieces[12] == '' or pieces[13] == '':
                    print "\nMISSING sample_count or is_in_spell or is_in_browser data for the following line: \n", line, "\n"
                    continue

                sample_count = int(pieces[11])
                is_in_spell = int(pieces[12])
                is_in_browser = int(pieces[13])
                if sample_count is None:
                    print "The sample_count column is None:", line
                    continue
                if is_in_spell is None:
                    print "The is_in_spell column is None:", line
                    continue
                elif is_in_spell > 1:
                    is_in_spell = 1
                if is_in_browser is None:
                    print "The is_in_browser column is None:", line
                    continue
                elif is_in_browser > 1:
                    is_in_browser = 1
                
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
                if pieces[5]:
                    date_public = pieces[5]
                    if "/" in date_public:
                        dates = date_public.split('/')
                        month = dates[0]
                        day = dates[1]
                        year = dates[2]
                        if len(month) == 1:
                            month = "0" + month
                        if len(day) == 1:
                            day = "0" + day
                        if len(year) == 2:
                            year = "20" + year
                        date_public = year + "-" + month + "-" + day 
                    data['date_public'] = date_public
                # if pieces[9]:
                #    taxid = pieces[9]
                #    if "|" in taxid:
                #        taxids = taxid.split('|')
                #        taxid = taxids[0]
                #    taxonomy_id = taxid_to_taxonomy_id.get("TAX:"+taxid)
                #    if taxonomy_id is None:
                #        print "The taxid: ", pieces[9], " is not in TAXONOMY table."
                #    else:
                #        data['taxonomy_id'] = taxonomy_id

                if parent_dataset_id:
                    data['parent_dataset_id'] = parent_dataset_id

                if pieces[10]:
                    data['channel_count'] = int(pieces[10])

                if pieces[14]:
                    desc_item = pieces[14].split(". ")
                    data['description']= desc_item[0]
                    desc_item.pop(0)
                    for desc in desc_item:
                        if data['description'].endswith('et al') or data['description'].endswith(' S') or data['description'] == 'S':
                            data['description'] = data['description'] + ". " + desc

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



