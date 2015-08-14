from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'sweng66'

key_switch = {'id': 'soid', 'name': 'display_name', 'def': 'description'}

def so_starter(bud_session_maker):
    
    terms = []
    parent_to_children = dict()
    ## check it out from  https://github.com/The-Sequence-Ontology/SO-Ontologies/
    f = open('src/sgd/convert/data/so-xp-simple.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'SO'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    type = quotation_split[2].split('[')[0].strip()
                    alias_type = type.split(' ')[0]
                    term['aliases'].append({'display_name': quotation_split[1], "alias_type": alias_type, "source": {"display_name": "SO"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'soid': term['soid'], 'display_name': term['display_name'], 'source': {'display_name': 'SO'}, 'ro_id': get_relation_to_ro_id('is a') })
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
    f.close()

    for term in terms:
        soid = term['soid']
        print soid
        term['children'] = [] if soid not in parent_to_children else parent_to_children[soid]
        term['urls'].append({'display_name': 'MISO',
                             'link': 'http://www.sequenceontology.org/miso/current_svn/term/' + term['soid'],
                             'source': {'display_name': 'OBO Foundry'},
                             'url_type': 'MISO'})
        term['urls'].append({'display_name': 'OLS',
                             'link': 'https://www.ebi.ac.uk/ontology-lookup/?termId=' + term['soid'],
                             'source': {'display_name': 'EBI'},
                             'url_type': 'OLS'})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, so_starter, 'so', lambda x: x['display_name'])




