from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'ecoid', 'name': 'display_name', 'def': 'description'}

def eco_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    is_obsolete_id = dict()
    source = 'ECO'
    ## downloaded from http://evidenceontology.googlecode.com/svn/trunk/eco.obo
    terms = read_obo('ECO', 
                     'src/sgd/convert/data/eco.obo',
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)

    for term in terms:
        if term['ecoid'] in is_obsolete_id:
            continue
        ecoid = term['ecoid']
        print ecoid
        if ecoid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[ecoid]:
                child_id = child['ecoid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
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




