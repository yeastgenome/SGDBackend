from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def ec_starter(bud_session_maker):

    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY

    ## downloaded from ftp.expasy.org/databases/enzyme/enzyme.dat
    file_name = "src/sgd/convert/data/enzyme.dat"
    f = open(file_name, 'rU')
    
    data = {}
    aliases = []
    alias = ''
    for line in f:
        if line.startswith("//") and data.get('display_name'):
            ## new entry
            data['ecid'] = data['display_name']
            data['description'] = data['description'].rstrip('.')
            data['source'] = {'display_name': 'ExPASy'}
            data['created_by'] = dbuser
            ec = data['display_name'].replace('EC:', '')
            data['urls'] = [ {'display_name': 'ExPASy',
                              'link': 'http://enzyme.expasy.org/EC/' + ec,
                              'source': {'display_name': 'ExPASy'},
                              'url_type': 'ExPASy',
                              'created_by': dbuser},
                             {'display_name': 'BRENDA',
                              'link': 'http://www.brenda-enzymes.org/php/result_flat.php4?ecno=' + ec,
                              'source': {'display_name': 'BRENDA'},
                              'url_type': 'BRENDA',
                              'created_by': dbuser} ]
            data['aliases'] = aliases

            yield data

            alias = ''
            aliases = []
            data = {}
            continue
            
        field = line.split('   ')
        if field[0] not in ['ID', 'DE', 'AN']:
            continue
        field[1] = field[1].rstrip()  
        if field[0] == 'ID' and 'n' not in field[1]:
            data['display_name'] = "EC:" + field[1]
        if data.get('display_name') and field[0] == 'DE':
            if data.get('description'):
                data['description'] = data['description'] + " " + field[1]
            else:
                data['description'] = field[1]
        if data.get('display_name') and field[0] == 'AN':
            if alias:
                alias = alias + " " + field[1]
            else:
                alias = field[1]
            if alias.endswith('.'):
                aliases.append({'display_name': alias.rstrip('.'),
                                'alias_type': 'Synonym',
                                'source': {'display_name': 'ExPASy'},
                                'created_by': dbuser
                              })
                alias = ''
   
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, ec_starter, 'ec', lambda x: x['display_name'])
