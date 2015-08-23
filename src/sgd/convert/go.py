from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'goid', 'name': 'display_name', 'namespace': 'go_namespace', 'def': 'description'}

def go_starter(bud_session_maker):
    
    parent_to_children = dict()
    source = 'GOC'
    is_obsolete_id = dict()
    ## downloaded from http://geneontology.org/ontology/go.obo
    f = open('src/sgd/convert/data/go.obo', 'r')
    terms = read_obo('GO',
                     'src/sgd/convert/data/go.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)
    
    for term in terms:
        goid = term['goid']
        if goid in is_obsolete_id:
            continue
        print goid
        if goid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[goid]:
                child_id = child['goid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        term['urls'].append({'display_name': term['goid'],
                             'link': 'http://amigo.geneontology.org/amigo/term/' + term['goid'],
                             'source': {'display_name': source},
                             'url_type': 'GO'})
        term['urls'].append({'display_name': 'View GO Annotations in other species in AmiGO',
                             'link': 'http://amigo.geneontology.org/amigo/term/' + term['goid'] + '#display-associations-tab',
                             'source': {'display_name': source},
                             'url_type': 'Amigo'})
        
        if term.get('display_name'):
            yield term

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, go_starter, 'go', lambda x: x['display_name'])




