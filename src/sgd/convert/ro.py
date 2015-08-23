from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'xref': 'roid', 'name': 'display_name', 'def': 'description'}

def ro_starter(bud_session_maker):

    parent_to_children = dict()
    source = 'GOC'
    is_obsolete_id = {}
    ## http://www.geneontology.org/ontology/extensions/gorel.obo
    [terms, roid2id] = read_obo('RO', 
                                'src/sgd/convert/data/gorel.obo', 
                                key_switch, 
                                parent_to_children, 
                                is_obsolete_id, 
                                source)

    for term in terms:
        if term.get('roid') == None or term.get('display_name') == None:
            continue
        roid = term['roid']
        if roid in is_obsolete_id:
            continue
        print roid
        id = roid2id.get(roid)
        if id not in parent_to_children:
            term['children'] = []
        else:
            children = []
            for child in parent_to_children[id]:
                child_roid = child['roid']
                if child_roid not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        roid = roid.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=RO&iri=http://purl.obolibrary.org/obo/' + roid,
                         'source': {'display_name': source},
                         'url_type': 'Ontobee'}]
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, ro_starter, 'ro', lambda x: x['display_name'])




