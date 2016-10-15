from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'roid', 'name': 'display_name', 'def': 'description'}

def ro_starter(bud_session_maker):

    parent_to_children = dict()
    source = 'GOC'
    is_obsolete_id = {}
    ## https://raw.githubusercontent.com/oborel/obo-relations/master/subsets/ro-chado.obo
    # [terms, roid2id] = read_obo('RO', 
    terms = read_obo('RO',
                     'src/sgd/convert/data/ro-chado.obo', 
                     key_switch, 
                     parent_to_children, 
                     is_obsolete_id, 
                     source)

    from src.sgd.convert import config

    dbuser = config.NEX_CREATED_BY

    for term in terms:

        if term.get('roid') == None or term.get('display_name') == None:
            continue
        roid = term['roid']
        if roid in is_obsolete_id:
            continue
        if roid.startswith('results'):
            continue

        term['display_name'] = term['display_name'].replace("_", " ").replace("'", "")

        print roid, term['display_name']
        
        if roid not in parent_to_children:
            term['children'] = []
        else:
            children = []
            for child in parent_to_children[roid]:
                if child['roid'].startswith('results'):
                    continue
                child_roid = child['roid']
                child['display_name'] = child['display_name'].replace("_", " ").replace("'", "")
                child['created_by'] = dbuser
                if child_roid not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        roid = roid.replace(":", "_")
        term['created_by'] = dbuser
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/ontology/RO?iri=http://purl.obolibrary.org/obo/' + roid,
                         'source': {'display_name': source},
                         'url_type': 'Ontobee',
                         'created_by': dbuser},
                        {'display_name': 'OLS',
                         'link': 'http://www.ebi.ac.uk/ols/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + roid,
                         'source': {'display_name': source},
                         'url_type': 'OLS',
                         'created_by': dbuser}]
        
        yield term

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, ro_starter, 'ro', lambda x: x['display_name'])




