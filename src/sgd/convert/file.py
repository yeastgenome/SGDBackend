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

    ## load README files first
    f = open('src/sgd/convert/data/published_datasets-files_metadata_A-O_201604.txt')
    for line in f:
        if line.startswith('bun_filepath'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            if pieces[11] != 'README' and pieces[11] != 'readme':
                continue
            display_name = pieces[3]
            if file_to_id.get(display_name):
                continue
            filepath_id = path_to_id.get(pieces[1])
            previous_file_name = pieces[2]
            status = pieces[4]
            topic_id = format_name_to_id.get(pieces[6].replace("topic:", "EDAM:").replace("topic_", "EDAM"))
            data_id = format_name_to_id.get(pieces[8].replace("data:", "EDAM:"))
            format_id = format_name_to_id.get(pieces[10].replace("format:", "EDAM:"))

            file_extension = pieces[11]
            file_date = pieces[12]
            is_public = int(pieces[13])
            is_in_spell = int(pieces[14])
            is_in_browser = int(pieces[15])
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

            if previous_file_name:
                data['previous_file_name'] = previous_file_name
            if filepath_id:
                data['filepath_id'] = filepath_id
            if description:
                data['description'] = description                

            yield data

    ## load other files
    file_to_id = dict([(x.display_name, x.id) for x in nex_session.query(File).all()])
    f.seek(0, 0)
    for line in f:
        if line.startswith('bun_filepath'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            if pieces[11] == 'README' or pieces[11] == 'readme':
                continue
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
            if pieces[6].startswith('NTR'):
                topic_id = display_name_to_id.get(pieces[5])
            if pieces[8].startswith('NTR'):
                data_id = display_name_to_id.get(pieces[7])
            if pieces[10].startswith('NTR'):
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
            is_public = int(pieces[13])
            is_in_spell = int(pieces[14])
            is_in_browser = int(pieces[15])
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

            if previous_file_name:
                data['previous_file_name'] = previous_file_name
            if filepath_id:
                data['filepath_id'] = filepath_id
            if readme_file_id:
                data['readme_file_id'] = readme_file_id
            if description:
                data['description'] = description

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
    basic_convert(config.BUD_HOST, config.NEX_HOST, file_starter, 'file', lambda x: (x['display_name'], x['file_date'], x['is_public'], x['is_in_spell'], x['is_in_browser'], x['file_extension'], x['data_id'], x['format_id'], x['topic_id']))



