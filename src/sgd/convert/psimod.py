from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'psimodid', 'name': 'display_name', 'def': 'description'}

def psimod_starter(bud_session_maker):
    
    parent_to_children = dict()
    source = 'EBI'
    is_obsolete_id = {}
    ## from http://psidev.cvs.sourceforge.net/viewvc/psidev/psi/mod/data/PSI-MOD.obo
    terms = read_obo('PSIMOD',
                     'src/sgd/convert/data/PSI-MOD.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)

    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY
    
    for term in terms:
        psimodid = term['psimodid']
        if psimodid in is_obsolete_id:
            continue
        if not psimodid.startswith('MOD:'):
            continue
        print psimodid
        if psimodid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[psimodid]:
                child_id = child['psimodid']
                if child_id not in is_obsolete_id:
                    child['created_by'] = dbuser
                    children.append(child)
            term['children'] = children
        term['created_by'] = dbuser
        link_id = psimodid.replace(':', '_')
        term['urls'].append({'display_name': 'BioPortal',
                             'link': 'https://bioportal.bioontology.org/ontologies/PSIMOD/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + link_id,
                             'source': {'display_name': 'BioPortal'},
                             'url_type': 'BioPortal',
                             'created_by': dbuser})
        term['urls'].append({'display_name': 'OLS',
                             'link': 'http://www.ebi.ac.uk/ols/ontologies/mod/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + link_id,
                             'source': {'display_name': 'OLS'},
                             'url_type': 'OLS',
                             'created_by': dbuser})
        term['urls'].append({'display_name': 'Ontobee',
                             'link': 'http://www.ontobee.org/ontology/MOD?iri=http://purl.obolibrary.org/obo/' + link_id,
                             'source': {'display_name': 'Ontobee'},
                             'url_type': 'Ontobee',
                             'created_by': dbuser})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, psimod_starter, 'psimod', lambda x: x['display_name'])




