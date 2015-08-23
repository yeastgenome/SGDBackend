from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'obiid', 'name': 'display_name', 'def': 'description'}

def obi_starter(bud_session_maker):
    
    parent_to_children = dict()
    is_obsolete_id = dict()
    source = 'OBI Consortium'
    ## http://www.berkeleybop.org/ontologies/obi.obo
    terms = read_obo('OBI', 
                     'src/sgd/convert/data/obi.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source)

    for term in terms:
        if term.get('obiid') == None or term.get('display_name') == None:
            continue
        obiid = term['obiid']
        if obiid in is_obsolete_id:
            continue
        print obiid
        if obiid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[obiid]:
                child_id = child['obiid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        term['source'] = { 'display_name': 'OBI Consortium'}
        obiid = obiid.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=OBI&iri=http://purl.obolibrary.org/obo/' + obiid,
                         'source': {'display_name': 'OBO Foundry'},
                         'url_type': 'Ontobee'}]
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, obi_starter, 'obi', lambda x: x['display_name'])




