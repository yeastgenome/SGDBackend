from src.sgd.convert import basic_convert

__author__ = 'sweng66'

key_switch = {'xref': 'ro_id', 'name': 'display_name', 'def': 'description'}

def ro_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## http://www.geneontology.org/ontology/extensions/gorel.obo
    f = open('src/sgd/convert/data/gorel.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Typedef]':
            if term is not None:
                terms.append(term)
            term = {}
        else:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'is_a' and term.get('display_name') and term.get('ro_id'):
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'ro_id': term['ro_id'], 'display_name': term['display_name'], 'source': {'display_name': 'GOC'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                    
    f.close()

    for term in terms:
        if term.get('ro_id') == None or term.get('display_name') == None:
            continue
        ro_id = term['ro_id']
        print ro_id
        term['children'] = [] if ro_id not in parent_to_children else parent_to_children[ro_id]
        term['source'] = { 'display_name': 'GOC'}
        ro_id = ro_id.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=RO&iri=http://purl.obolibrary.org/obo/' + ro_id,
                         'source': {'display_name': 'GOC'},
                         'url_type': 'Ontobee'}]
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, ro_starter, 'ro', lambda x: x['display_name'])




