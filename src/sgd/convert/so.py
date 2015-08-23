from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'soid', 'name': 'display_name', 'def': 'description'}

def so_starter(bud_session_maker):
    
    parent_to_children = dict()
    source = 'SO'
    is_obsolete_id = {}
    ## check it out from  https://github.com/The-Sequence-Ontology/SO-Ontologies/
    terms = read_obo('SO',
                     'src/sgd/convert/data/so-xp-simple.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)
    
    for term in terms:
        soid = term['soid']
        if soid in is_obsolete_id:
            continue
        print soid
        if soid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[soid]:
                child_id = child['soid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
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




