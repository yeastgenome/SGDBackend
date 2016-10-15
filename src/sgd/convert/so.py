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

    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY
    
    for term in terms:
        soid = term['soid']
        if soid in is_obsolete_id:
            continue
        if not soid.startswith('SO:'):
            continue
        print soid
        if soid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[soid]:
                child_id = child['soid']
                if child_id not in is_obsolete_id:
                    child['created_by'] = dbuser
                    children.append(child)
            term['children'] = children

        term['created_by'] = dbuser
        aliases = []
        for alias in term['aliases']:
            alias['created_by'] = dbuser
            aliases.append(alias)
        term['aliases'] = aliases
        soid = term['soid'].replace(":", "_")
        term['urls'].append({'display_name': 'MISO',
                             'link': 'http://www.sequenceontology.org/miso/current_svn/term/' + term['soid'],
                             'source': {'display_name': 'MISO'},
                             'url_type': 'MISO',
                             'created_by': dbuser})
        term['urls'].append({'display_name': 'OLS',
                             'link': 'http://www.ebi.ac.uk/ols/ontologies/so/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + soid,
                             'source': {'display_name': 'OLS'},
                             'url_type': 'OLS',
                             'created_by': dbuser})
        term['urls'].append({'display_name': 'Ontobee',
                             'link': 'http://www.ontobee.org/ontology/SO?iri=http://purl.obolibrary.org/obo/' + soid,
                             'source': {'display_name': 'Ontobee'},
                             'url_type': 'Ontobee',
                             'created_by': dbuser})
        term['urls'].append({'display_name': 'BioPortal',
                             'link': 'https://bioportal.bioontology.org/ontologies/SO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + soid,
                             'source': {'display_name': 'BioPortal'},
                             'url_type': 'BioPortal',
                             'created_by': dbuser})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, so_starter, 'so', lambda x: x['display_name'])




