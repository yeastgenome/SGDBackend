from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'apoid', 'name': 'display_name', 'namespace': 'apo_namespace', 'def': 'description'}

def apo_starter(bud_session_maker):

    parent_to_children = dict()
    is_obsolete_id = dict()
    source = 'SGD'
    ## downloaded from http://bioportal.bioontology.org/ontologies/APO
    terms = read_obo('APO', 
                     'src/sgd/convert/data/ascomycete_phenotype.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)
    
    for term in terms:
        if term['apoid'] in is_obsolete_id:
            continue
        apoid = term['apoid']
        print apoid
        if apoid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[apoid]:
                child_id = child['apoid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        apoid = apoid.replace(':', '_')
        term['urls'].append({'display_name': 'BioPortal',
                             'link': 'http://bioportal.bioontology.org/ontologies/APO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + apoid,
                             'source': {'display_name': 'BioPortal'},
                             'url_type': 'BioPortal'})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, apo_starter, 'apo', lambda x: x['display_name'])




