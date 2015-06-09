from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'

key_switch = {'id': 'efo_id', 'name': 'name', 'def': 'description', 'created_by': 'created'}

def experimentfactor_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    f = open('src/sgd/convert/data/efo.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'name': 'EBI'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    display_name = quotation_split[1]
                    alias_type =  quotation_split[2].split('[')[0].strip()
                    if len(display_name) < 900 and alias_type in {'BROAD', 'EXACT', 'RELATED', 'NARROW'}:
                        term['aliases'].append({'name': display_name, "alias_type": alias_type, "source": {"name": "EBI"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'efo_id': term['efo_id'], 'name': term['name'], 'source': {'name': 'EBI'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                elif pieces[0] != 'created_by':
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        efo_id = term['efo_id']
        term['children'] = [] if efo_id not in parent_to_children else parent_to_children[efo_id]
        term['urls'].append({'name': 'OLS',
                              'link': 'https://www.ebi.ac.uk/ontology-lookup/?termId=' + term['efo_id'],
                              'source': {'name': 'EBI'},
                              'url_type': 'External'})
        if 'description' in term and len(term['description']):
            term['description'] = term['description'][:1000]
        yield term

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, experimentfactor_starter, 'experimentfactor', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

