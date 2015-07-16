from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def enzyme_starter(bud_session_maker):

    ## downloaded from ftp.expasy.org/databases/enzyme/enzyme.dat
    file_name = "src/sgd/convert/data/enzyme.dat"
    f = open(file_name, 'rU')
    
    data = {}
    aliases = []
    alias = ''
    for line in f:
        if line.startswith("//") and data.get('display_name'):
            ## new entry
            data['description'] = data['description'].rstrip('.')
            data['source'] = {'display_name': 'ExPASy'}
            data['urls'] = [ {'display_name': 'ExPASy',
                              'link': 'http://enzyme.expasy.org/EC/' + data['display_name'],
                              'source': {'display_name': 'ExPASy'},
                              'url_type': 'ExPASy'},
                             {'display_name': 'BRENDA',
                              'link': 'http://www.brenda-enzymes.org/php/result_flat.php4?ecno=' + data['display_name'],
                              'source': {'display_name': 'BRENDA'},
                              'url_type': 'BRENDA'} ]
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
            data['display_name'] = field[1]
        if data.get('display_name') != None and field[0] == 'DE':
            if data.get('description') != None:
                data['description'] = data['description'] + " " + field[1]
            else:
                data['description'] = field[1]
        if data.get('display_name') != None and field[0] == 'AN':
            if alias:
                alias = alias + " " + field[1]
            else:
                alias = field[1]
            if alias.endswith('.'):
                aliases.append({'display_name': alias.rstrip('.'),
                                'alias_type': 'Synonym',
                                'source': {'display_name': 'ExPASy'}
                              })
                alias = ''
   
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, enzyme_starter, 'enzyme', lambda x: x['display_name'])
