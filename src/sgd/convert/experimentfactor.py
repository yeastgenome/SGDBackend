from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'

key_switch = {'id': 'efo_id', 'name': 'display_name', 'def': 'description', 'created_by': 'created'}

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
                    'source': {'display_name': 'EBI'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    display_name = quotation_split[1]
                    if len(display_name) < 900:
                        term['aliases'].append({'display_name': display_name, "alias_type": quotation_split[2].split('[')[0].strip(), "source": {"display_name": "EBI"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'efo_id': term['efo_id'], 'display_name': term['display_name'], 'source': {'display_name': 'EBI'}, 'relation_type': 'is_a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                elif pieces[0] != 'created_by':
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        efo_id = term['efo_id']
        print efo_id
        term['children'] = [] if efo_id not in parent_to_children else parent_to_children[efo_id]
        term['urls'].append({'display_name': 'OLS',
                              'link': 'https://www.ebi.ac.uk/ontology-lookup/?termId=' + term['efo_id'],
                              'source': {'display_name': 'EBI'},
                              'url_type': 'External'})
        if 'description' in term and len(term['description']):
            term['description'] = term['description'][:1000]
        yield term

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, experimentfactor_starter, 'experimentfactor', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

