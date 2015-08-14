from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'sweng66'

key_switch = {'id': 'apoid', 'name': 'display_name', 'namespace': 'apo_namespace', 'def': 'description'}

def apo_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## downloaded from http://bioportal.bioontology.org/ontologies/APO
    f = open('src/sgd/convert/data/ascomycete_phenotype.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'SGD'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    type = quotation_split[2].split('[')[0].strip()
                    alias_type = type.split(' ')[0]
                    term['aliases'].append({'display_name': quotation_split[1], "alias_type": alias_type, "source": {"display_name": "SGD"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()                    
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'apoid': term['apoid'], 'display_name': term['display_name'], 'apo_namespace': term['apo_namespace'],'source': {'display_name': 'GOC'}, 'ro_id': get_relation_to_ro_id('is a')})
                elif pieces[0] in key_switch:
                    text = pieces[1].strip()
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
        apoid = term['apoid']
        print apoid
        term['children'] = [] if apoid not in parent_to_children else parent_to_children[apoid]
        apoid = apoid.replace(':', '_')
        term['urls'].append({'display_name': 'BioPortal',
                             'link': 'http://bioportal.bioontology.org/ontologies/APO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + apoid,
                             'source': {'display_name': 'BioPortal'},
                             'url_type': 'BioPortal'})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, apo_starter, 'apo', lambda x: x['display_name'])




