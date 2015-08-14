from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'sweng66'

key_switch = {'id': 'goid', 'name': 'display_name', 'namespace': 'go_namespace', 'def': 'description'}

def go_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## downloaded from http://geneontology.org/ontology/go.obo
    f = open('src/sgd/convert/data/go.obo', 'r')
    term = None
    parent_child_pair = {}
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'GOC'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    type = quotation_split[2].split('[')[0].strip()
                    alias_type = type.split(' ')[0]
                    term['aliases'].append({'display_name': quotation_split[1], "alias_type": alias_type, "source": {"display_name": "GOC"}})
                elif pieces[0] == 'is_a' or pieces[0] == 'relationship':
                    if term.get('display_name') is None:
                        continue
                    # is_a: GO:0051231 ! spindle elongation
                    # relationship: part_of GO:0015767 ! lactose transport
                    parent = pieces[1].split('!')[0].strip()
                    relation_type = 'is a'
                    if pieces[0] == 'relationship':
                        type_goid = parent.split(' ')
                        relation_type = type_goid[0].replace('_', ' ')
                        parent = type_goid[1].strip()
                    if (parent, term['goid']) in parent_child_pair:
                        continue
                    parent_child_pair[(parent, term['goid'])] = 1
                    ro_id = get_relation_to_ro_id(relation_type)
                    if ro_id is None:
                        print relation_type, " is not in RO table"
                        continue
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'goid': term['goid'], 'display_name': term['display_name'], 'go_namespace': term['go_namespace'],'source': {'display_name': 'GOC'}, 'ro_id': ro_id})
                elif pieces[0] in key_switch:
                    text = pieces[1].strip()
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    elif pieces[0] == 'namespace':
                        text = text.replace('_', ' ')
                    term[key_switch[pieces[0]]] = text
                elif pieces[0] == 'is_obsolete':
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        if term.get('is_obsolete'):
            continue
        goid = term['goid']
        print goid
        term['children'] = [] if goid not in parent_to_children else parent_to_children[goid]
        term['urls'].append({'display_name': term['goid'],
                             'link': 'http://amigo.geneontology.org/amigo/term/' + term['goid'],
                             'source': {'display_name': 'GOC'},
                             'url_type': 'GO'})
        term['urls'].append({'display_name': 'View GO Annotations in other species in AmiGO',
                             'link': 'http://amigo.geneontology.org/amigo/term/' + term['goid'] + '#display-associations-tab',
                             'source': {'display_name': 'GOC'},
                             'url_type': 'Amigo'})
        
        if term.get('display_name'):
            yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, go_starter, 'go', lambda x: x['display_name'])




