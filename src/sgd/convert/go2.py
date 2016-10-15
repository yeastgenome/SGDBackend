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

    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY

    from src.sgd.model.nex.go import Go
    
    nex_session = get_nex_session()
    goid_to_id = dict([(x.goid, x.id) for x in nex_session.query(Go).all()])
    nex_session.close()

    for term in terms:
        goid = term['goid']
        if goid in is_obsolete_id:
            continue
        if not goid.startswith('GO:'):
            continue



        if goid in goid_to_id:
            continue



        print goid
        if goid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[goid]:
                child_id = child['goid']
                if not child_id.startswith('GO:'):
                    continue
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
        term['urls'].append({'display_name': term['goid'],
                             'link': 'http://amigo.geneontology.org/amigo/term/' + term['goid'],
                             'source': {'display_name': source},
                             'url_type': 'GO',
                             'created_by': dbuser})
        term['urls'].append({'display_name': 'View GO Annotations in other species in AmiGO',
                             'link': 'http://amigo.geneontology.org/amigo/term/' + term['goid'] + '#display-associations-tab',
                             'source': {'display_name': source},
                             'url_type': 'Amigo',
                             'created_by': dbuser})
        
        if term.get('display_name'):
            yield term


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, go_starter, 'go', lambda x: x['display_name'])




