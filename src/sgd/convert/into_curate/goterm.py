from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kpaskov'

key_switch = {'id': 'go_id', 'name': 'name', 'def': 'description', 'namespace': 'go_aspect', 'created_by': 'created'}

def goterm_starter(bud_session_maker):

    terms = []
    parent_to_children = dict()
    f = open('src/sgd/convert/data/go.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'name': 'GO'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    display_name = quotation_split[1]
                    alias_type = quotation_split[2].split('[')[0].strip()
                    if len(display_name) < 500 and alias_type in {'BROAD', 'EXACT', 'RELATED', 'NARROW'} and (display_name, alias_type) not in [(x['name'], x['alias_type']) for x in term['aliases']]:
                        term['aliases'].append({'name': display_name, "alias_type": alias_type, "source": {"name": "GO"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'go_id': term['go_id'], 'source': {'name': 'GO'}, 'go_aspect': term['go_aspect'].replace('_', ' '), 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                else:
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        go_id = term['go_id']
        term['children'] = [] if go_id not in parent_to_children else parent_to_children[go_id]
        term['urls'].append({'name': term['go_id'],
                              'link': "http://amigo.geneontology.org/amigo/term/" + term['go_id'],
                              'source': {'name': 'GO'},
                              'url_type': 'GO'})
        term['urls'].append({'name': 'View GO Annotations in other species in AmiGO',
                              'link': "http://amigo.geneontology.org/amigo/term/" + term['go_id'] + "#display-associations-tab",
                              'source': {'name': 'GO'},
                              'url_type': 'Amigo'})
        term['go_aspect'] = term['go_aspect'].replace('_', ' ')
        if 'description' in term and len(term['description']) > 1000:
            term['description'] = term['description'][:1000]
        yield term


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, goterm_starter, 'goterm', lambda x: x['go_id'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

