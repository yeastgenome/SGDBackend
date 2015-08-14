from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'sweng66'

key_switch = {'id': 'ecoid', 'name': 'display_name', 'def': 'description'}

def eco_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## downloaded from http://evidenceontology.googlecode.com/svn/trunk/eco.obo
    f = open('src/sgd/convert/data/eco.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'ECO'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    term['aliases'].append({'display_name': quotation_split[1], "alias_type": quotation_split[2].split('[')[0].strip(), "source": {"display_name": "ECO"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'ecoid': term['ecoid'], 'display_name': term['display_name'], 'source': {'display_name': 'ECO'}, 'ro_id': get_relation_to_ro_id('is a')})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                elif pieces[0] == 'is_obsolete':
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        if term.get('is_obsolete'):
            continue
        ecoid = term['ecoid']
        print ecoid
        term['children'] = [] if ecoid not in parent_to_children else parent_to_children[ecoid]
        term['urls'].append({'display_name': 'BioPortal',
                              'link': 'http://bioportal.bioontology.org/ontologies/ECO?p=classes&conceptid=' + term['ecoid'],
                              'source': {'display_name': 'BioPortal'},
                              'url_type': 'BioPortal'})
        term['urls'].append({'display_name': 'OLS',
                              'link': 'http://www.ebi.ac.uk/ontology-lookup/?termId=' + term['ecoid'],
                              'source': {'display_name': 'EBI'},
                              'url_type': 'OLS'})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, eco_starter, 'eco', lambda x: x['display_name'])




