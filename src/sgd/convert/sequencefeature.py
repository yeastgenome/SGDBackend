from src.sgd.convert import basic_convert

__author__ = 'kpaskov'
## updated by sweng66

key_switch = {'id': 'so_id', 'name': 'display_name', 'def': 'description'}

def sequencefeature_starter(bud_session_maker):
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
                    parent_to_children[parent].append({'so_id': term['so_id'], 'display_name': term['display_name'], 'source': {'display_name': 'SO'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                # else:
                #    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        so_id = term['so_id']
        print so_id
        term['children'] = [] if so_id not in parent_to_children else parent_to_children[so_id]
        term['urls'].append({'display_name': 'MISO',
                              'link': 'http://www.sequenceontology.org/miso/current_svn/term/' + term['so_id'],
                              'source': {'display_name': 'OBO Foundry'},
                              'url_type': 'MISO'})
        term['urls'].append({'display_name': 'OLS',
                              'link': 'https://www.ebi.ac.uk/ontology-lookup/?termId=' + term['so_id'],
                              'source': {'display_name': 'EBI'},
                              'url_type': 'OLS'})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, sequencefeature_starter, 'sequencefeature', lambda x: x['display_name'])




