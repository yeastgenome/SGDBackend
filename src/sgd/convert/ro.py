from src.sgd.convert import basic_convert

__author__ = 'sweng66'

key_switch = {'xref': 'roid', 'name': 'display_name', 'def': 'description'}

def ro_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## http://www.geneontology.org/ontology/extensions/gorel.obo
    f = open('src/sgd/convert/data/gorel.obo', 'r')
    term = None
    roid2id = {}
    id = ''
    for line in f:
        line = line.strip()
        if line == '[Typedef]':
            if term is not None:
                terms.append(term)
            term = {}
        else:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'id':
                    id = pieces[1]
                elif pieces[0] == 'is_a' and term.get('display_name') and term.get('roid'):
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'roid': term['roid'], 'display_name': term['display_name'], 'source': {'display_name': 'GOC'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'name':
                        text = text.replace("_", " ")
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    if pieces[0] == 'xref':
                        roid2id[pieces[1]] = id
                        id = ''
                    term[key_switch[pieces[0]]] = text
                    
    f.close()

    for term in terms:
        if term.get('roid') == None or term.get('display_name') == None:
            continue
        roid = term['roid']
        print roid
        id = roid2id.get(roid)
        term['children'] = [] if id not in parent_to_children else parent_to_children[id]
        term['source'] = { 'display_name': 'GOC'}
        roid = roid.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=RO&iri=http://purl.obolibrary.org/obo/' + roid,
                         'source': {'display_name': 'GOC'},
                         'url_type': 'Ontobee'}]
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, ro_starter, 'ro', lambda x: x['display_name'])




