from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'doid', 'name': 'display_name', 'def': 'description'}

def disease_starter(bud_session_maker):

    parent_to_children = dict()
    is_obsolete_id = dict()
    source = 'DO'
    ## https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid.obo
    terms = read_obo('DO', 
                     'src/sgd/convert/data/doid.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source, 
                     source)
    
    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY

    found = {}
    found_url = {}
    for term in terms:
        if term['doid'] in is_obsolete_id:
            continue
        doid = term['doid']
        print doid
        if doid in found:
            continue
        if not doid.startswith("DOID:"):
            continue
        found[doid] = 1
        if doid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[doid]:
                child_id = child['doid']
                child['created_by'] = dbuser
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        term['created_by'] = dbuser
        aliases = []
        for alias in term['aliases']:
            alias['created_by'] = dbuser
            aliases.append(alias)
        term['aliases'] = aliases
        doid2 = doid.replace(':', '_')
        url = 'http://www.disease-ontology.org/?id=' + doid  
        if url not in found_url:
            term['urls'].append({'display_name': 'DO',
                                 'link': 'http://www.disease-ontology.org/?id=' + doid,
                                 'source': {'display_name': 'DO'},
                                 'url_type': 'DO',
                                 'created_by': dbuser})
            term['urls'].append({'display_name': 'BioPortal',
                                 'link': 'http://bioportal.bioontology.org/ontologies/DOID/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + doid2,
                                 'source': {'display_name': 'BioPortal'},
                                 'url_type': 'BioPortal',
                                 'created_by': dbuser})
            term['urls'].append({'display_name': 'OLS',
                                 'link': 'http://www.ebi.ac.uk/ols/ontologies/doid/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + doid2,
                                 'source': {'display_name': 'OLS'},
                                 'url_type': 'OLS',
                                 'created_by': dbuser})
            term['urls'].append({'display_name': 'Ontobee',
                                 'link': 'http://www.ontobee.org/ontology/DOID?iri=http://purl.obolibrary.org/obo/' + doid2,
                                 'source': {'display_name': 'Ontobee'},
                                 'url_type': 'Ontobee',
                                 'created_by': dbuser})
        found_url[url] = 1

        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, disease_starter, 'disease', lambda x: x['display_name'])




