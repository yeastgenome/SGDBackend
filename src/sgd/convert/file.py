from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def file_starter(bud_session_maker):

    from src.sgd.model.nex.file import File
    from src.sgd.model.nex.filepath import Filepath
    from src.sgd.model.nex.edam import Edam

    nex_session = get_nex_session()

    file_to_id = dict([(x.display_name, x.id) for x in nex_session.query(File).all()])
    path_to_id = dict([(x.filepath, x.id) for x in nex_session.query(Filepath).all()])
    format_name_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Edam).all()]) 
    display_name_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Edam).all()])

    readme_data = []
    other_data = []

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
                display_name = pieces[3]
                if file_to_id.get(display_name):
                    continue
                filepath_id = path_to_id.get(pieces[1])
                previous_file_name = pieces[2]
                status = pieces[4]
                if status == 'Archive':
                    status = 'Archived'
                topic_id = format_name_to_id.get(pieces[6].replace("topic:", "EDAM:").replace("topic_", "EDAM:"))
                data_id = format_name_to_id.get(pieces[8].replace("data:", "EDAM:"))
                format_id = format_name_to_id.get(pieces[10].replace("format:", "EDAM:"))
                if topic_id is None or pieces[6].startswith('NTR'):
                    topic_id = display_name_to_id.get(pieces[5])
                if data_id is None or pieces[8].startswith('NTR'):
                    data_id = display_name_to_id.get(pieces[7])
                if format_id is None or pieces[10].startswith('NTR'):
                    format_id= display_name_to_id.get(pieces[9])
                if topic_id is None:
                    print "No TOPIC edam id provided.", line
                    continue
                if data_id is None:
                    print "No DATA edam id provided.", line
                    continue
                if format_id is None:
                    print "No FORMAT edam id provided.", line
                    continue
                file_extension = pieces[11]
                file_date = pieces[12]
                if file_date == '':
                    print "No file_date provided:", line
                    continue
                if "/" in file_date:
                    file_date = reformat_date(file_date)
                
                is_public = int(pieces[13])
                is_in_spell = int(pieces[14])
                is_in_browser = int(pieces[15])
                readme_file_id = None
                if pieces[16]:
                    readme_file_id = file_to_id.get(pieces[16])

                description = pieces[17].replace('"', '')

                data = { 'source': { 'display_name': 'SGD' },
                         'display_name': display_name,
                         'dbentity_status': status,
                         'data_id': data_id,
                         'format_id': format_id,
                         'file_date': file_date,
                         'is_public': is_public,
                         'is_in_spell': is_in_spell,
                         'is_in_browser': is_in_browser,
                         'file_extension': file_extension,
                         'topic_id': topic_id }

                if previous_file_name and "|" not in previous_file_name:
                    data['previous_file_name'] = previous_file_name
                if filepath_id:
                    data['filepath_id'] = filepath_id
                if readme_file_id:
                    data['readme_file_id'] = readme_file_id
                if description:
                    data['description'] = description

                if pieces[11] != 'README' and pieces[11] != 'readme':   
                    other_data.append(data)
                # else:
                #   readme_data.append(data)

        f.close()

    # for data in readme_data:
    #    yield data
    # file_to_id = dict([(x.display_name, x.id) for x in nex_session.query(File).all()])

    for data in other_data:
        yield data

def reformat_date(file_date):

    dates = file_date.split("/")
    month = dates[0]
    day= dates[1]
    year = dates[2]
    if len(year) == 2:
        year = "20" + year
    if len(month) == 1:
        month ="0" + month
    if len(day) == 1:
        day = "0" + day

    return year + "-" + month + "-" + day


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, file_starter, 'file', lambda x: (x['display_name'], x['file_date'], x['is_public'], x['is_in_spell'], x['is_in_browser'], x['file_extension'], x['data_id'], x['format_id'], x['topic_id']))



