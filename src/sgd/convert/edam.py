from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def chebi_starter(bud_session_maker):

    chebi_to_date_created = {}
        
    parent_to_children = dict()
    source = 'EMBI'
    ontology = 'EDAM'
    is_obsolete_id = dict()
    # downloaded from http://edamontology.org/EDAM.owl
    file = 'src/sgd/convert/data/EDAM.owl'
    terms = read_owl(file, 
                     parent_to_children,
                     is_obsolete_id,
                     source)

    loaded = []

    for term in terms:

        name = term['display_name']
        loaded.append(name.lower())

        edamid = term['edamid']
        if edamid in is_obsolete_id:
            continue
        print edamid
        if edamid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[edamid]:
                child_id = child['edamid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
            id = term['edamid'].replace('EDAM:', '')
            link_id = term['edam_namespace'] + '_' + id 
        term['urls'] = [{'display_name': 'BioPortal',
                         'link': 'http://bioportal.bioontology.org/ontologies/EDAM?p=classes&conceptid=' + link_id,
                         'source': {'display_name': source},
                         'url_type': 'BioPortal'}]
        term['urls'].append({'display_name': 'Ontobee',
                             'link': 'http://www.ontobee.org/ontology/EDAM?iri=http://edamontology.org/' + link_id,
                             'source': {'display_name': source},
                             'url_type': 'Ontobee'})
        yield term


def read_owl(filename, parent_to_children, is_obsolete_id, source):

    from src.sgd.convert.util import get_relation_to_ro_id
    ro_id = get_relation_to_ro_id('is a')

    terms = []
    f = open(filename, 'r')
    term = None
    parent_child_pair = {}

    start_ontology = 0

    for line in f:
        line = line.strip()
        if ontology == 'EDAM' and '<owl:Class rdf:about="http://edamontology.org/' in line:
            start_ontology = 1
            line = line.replace('<owl:Class rdf:about="http://edamontology.org/', '')
            line = line.replace('"', '')
            line = line.replace('>', '')
            pieces = line.split('_')
            term = { 'source': { 'display_name': source },
                     'edamid': 'EDAM:' + pieces[1],
                     'format_name': 'EDAM:' + pieces[1],
                     'edam_namespace': pieces[0] }
            continue
        if '</owl:Class>' in line:
            start_ontology = 0 
            if term is not None:
                terms.append(term)
                term = None
            continue
        if start_ontology == 0:
            continue
        if '<rdfs:label>' in line:
            line = line.replace('<rdfs:label>', '')
            line = line.replace('</rdfs:label>', '')
            term['display_name'] = line
        if '<ExactSynonym>' in line or 'BroadSynonym' in line or 'NarrowSynonym' in line or 'RelatedSynonym' in line:
            if 'aliases' not in term:
                term['aliases'] = []
            pieces = line.split('>')
            alias_name = pieces[1].split('<')[0]
            alias_type = pieces[0].replace('<oboInOwl:has', '')
            alias_type = alias_type.replace('Synonym', '')
            alias_type = alias_type.upper()            
            term['aliases'].append({'display_name': alias_name, 
                                    "alias_type": alias_type, 
                                    "source": {"display_name": source}})  
        if '<oboInOwl:hasDefinition>' in line:
            line = line.replace('<oboInOwl:hasDefinition>', '')
            line = line.replace('</oboInOwl:hasDefinition>', '')
            term['description'] = line
        if '<rdfs:subClassOf rdf:resource="http://edamontology.org/' in line:
            line = line.replace('<rdfs:subClassOf rdf:resource="http://edamontology.org/', '')
            line = line.replace('"', '')
            line = line.replace('>', '')
            pieces = line.split('_')
            parent = 'EDAM:' + pieces[1]
            if parent not in parent_to_children:
                parent_to_children[parent] = []
            parent_to_children[parent].append({'edamid': term['edamid'], 
                                               'display_name': term['display_name'],
                                               'format_name': term['format_name'],
                                               'edam_namespace': term['edam_namespace'],
                                               'description': term['description'],
                                               'source': {'display_name': source}, 
                                               'ro_id': ro_id})
        if 'obsolete_since' in line:
            is_obsolete_id[term['edamid']] = 1

    f.close()

    return terms        
                

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, edam_starter, 'edam', lambda x: x['display_name'])


