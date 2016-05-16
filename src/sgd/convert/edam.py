from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def edam_starter(bud_session_maker):
        
    parent_to_children = dict()
    source = 'EDAM'
    is_obsolete_id = dict()
    # downloaded from http://edamontology.org/EDAM.owl
    file = 'src/sgd/convert/data/EDAM.owl'
    terms = read_owl(file, 
                     parent_to_children,
                     is_obsolete_id,
                     source)

    loaded = []

    for term in terms:

        name = term.get('display_name')
        if name is None:
            print "no name found for ", term['edamid']
            continue
        loaded.append(name.lower())

        edamid = term['edamid']
        namespace = term['edam_namespace']
        if (edamid, namespace) in is_obsolete_id:
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

    ## add NTR terms:
    f = open('src/sgd/convert/data/published_datasets-files_metadata_A-O_201604.txt')
    found = {}
    i = 0
    for line in f:
        if line.startswith('bun_filepath'):
            continue
        line = line.strip()
        if line:
            pieces = line.split("\t")
            if pieces[6].startswith('NTR'):
                namespace = 'topic'
                display_name = pieces[5]
                if (namespace, display_name) not in found:
                    i = i + 1
                    found[(namespace, display_name)] = 1
                    yield { 'source': { 'display_name': 'SGD' },
                            'edamid': 'NTR:' + str(i),
                            'format_name': 'NTR:' + str(i),
                            'edam_namespace': namespace,
                            'display_name': display_name }
            if pieces[8].startswith('NTR'):
                namespace = 'data'
                display_name = pieces[7]
                if (namespace, display_name) not in found:
                    i = i + 1
                    found[(namespace, display_name)] = 1
                    yield { 'source': { 'display_name': 'SGD' },
                            'edamid': 'NTR:' + str(i),
                            'format_name': 'NTR:' + str(i),
                            'edam_namespace': namespace,
                            'display_name': display_name }
            if pieces[10].startswith('NTR'):
                namespace = 'format'
                display_name = pieces[9]
                if (namespace, display_name) not in found:
                    i = i + 1
                    found[(namespace, display_name)] = 1
                    yield { 'source': { 'display_name': 'SGD' },
                            'edamid': 'NTR:' + str(i),
                            'format_name': 'NTR:' + str(i),
                            'edam_namespace': namespace,
                            'display_name': display_name }


def read_owl(filename, parent_to_children, is_obsolete_id, source):

    from src.sgd.convert.util import get_relation_to_ro_id
    ro_id = get_relation_to_ro_id('is a')

    terms = []
    f = open(filename, 'r')
    term = None
    parent_child_pair = {}

    start_ontology = 0
    parents = []
    for line in f:
        line = line.strip()
        if '<owl:Class rdf:about="http://edamontology.org/' in line:
            start_ontology = 1
            line = line.replace('<owl:Class rdf:about="http://edamontology.org/', '')
            line = line.replace('"', '')
            line = line.replace('>', '')
            pieces = line.split('_')
            term = { 'source': { 'display_name': source },
                     'edamid': 'EDAM:' + pieces[1],
                     'format_name': 'EDAM:' + pieces[1],
                     'edam_namespace': pieces[0],
                     'aliases': []}
            continue
        if '</owl:Class>' in line:
            start_ontology = 0 
            if term is not None:
                if len(parents) > 0 and term.get('display_name') is not None:
                    for parent in parents:
                        if parent not in parent_to_children:
                            parent_to_children[parent] = []
                        parent_to_children[parent].append({'edamid': term['edamid'],
                                                           'format_name': term['format_name'],
                                                           'display_name': term.get('display_name'),
                                                           'edam_namespace': term['edam_namespace'],
                                                           'source': {'display_name': source}, 
                                                           'description': "CHILD:" + str(term.get('description')),
                                                           'ro_id': ro_id})
                terms.append(term)
                parents = []
                term = None
            continue

        if start_ontology == 0:
            continue
        if '<rdfs:label>' in line:
            line = line.replace('<rdfs:label>', '')
            line = line.replace('</rdfs:label>', '')
            term['display_name'] = line
        if 'ExactSynonym' in line or 'BroadSynonym' in line or 'NarrowSynonym' in line or 'RelatedSynonym' in line:
            if 'aliases' not in term:
                term['aliases'] = []
            pieces = line.split('>')
            alias_name = pieces[1].split('<')[0]
            alias_type = pieces[0].replace('<oboInOwl:has', '')
            alias_type = alias_type.replace('Synonym', '')
            alias_type = alias_type.upper()            

            if alias_name == '':
                # print "ALIAS LINE: ", line
                # print "ALIAS TYPE: ", alias_type
                # print "ALIAS NAME: ", alias_name, "\n"
                continue
            term['aliases'].append({"display_name": alias_name, 
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
            parent = 'EDAM:' + pieces[1].replace('/', '')
            parents.append(parent)
        if 'obsolete_since' in line:
            is_obsolete_id[(term['edamid'], term['edam_namespace'])] = 1

    f.close()

    return terms        
                

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, edam_starter, 'edam', lambda x: x['display_name'])


