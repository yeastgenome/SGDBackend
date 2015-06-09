from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'

key_switch = {'id': 'eco_id', 'name': 'name', 'def': 'description'}

def evidence_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    f = open('src/sgd/convert/data/eco.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'name': 'ECO'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    term['aliases'].append({'name': quotation_split[1], "alias_type": quotation_split[2].split('[')[0].strip(), "source": {"name": "ECO"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'eco_id': term['eco_id'], 'name': term['name'], 'source': {'name': 'ECO'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                else:
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        eco_id = term['eco_id']
        term['children'] = [] if eco_id not in parent_to_children else parent_to_children[eco_id]
        term['urls'].append({'name': 'BioPortal',
                              'link': 'http://bioportal.bioontology.org/ontologies/ECO?p=classes&conceptid=' + term['eco_id'],
                              'source': {'name': '-'},
                              'url_type': 'External'})
        term['urls'].append({'name': 'OLS',
                              'link': 'http://www.ebi.ac.uk/ontology-lookup/?termId=' + term['eco_id'],
                              'source': {'name': 'EBI'},
                              'url_type': 'External'})
        yield term

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, evidence_starter, 'evidence', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

