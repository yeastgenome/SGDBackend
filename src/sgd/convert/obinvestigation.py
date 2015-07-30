from src.sgd.convert import basic_convert

__author__ = 'sweng66'

key_switch = {'id': 'obi_id', 'name': 'display_name', 'def': 'description'}

def obinvestigation_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## http://www.berkeleybop.org/ontologies/obi.obo
    f = open('src/sgd/convert/data/obi.obo', 'r')
    term = None
    for line in f:
        if line.startswith('property_value') or line.startswith('owl-'):
            continue
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {}
        # elif term is not None:
        else:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'is_a' and term.get('display_name') and term.get('obi_id'):
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'obi_id': term['obi_id'], 'display_name': term['display_name'], 'source': {'display_name': 'OBI Consortium'}, 'relation_type': 'is a'})
                    # print parent_to_children[parent]
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                    
    f.close()

    for term in terms:
        if term.get('obi_id') == None or term.get('display_name') == None:
            continue
        obi_id = term['obi_id']
        print obi_id
        term['children'] = [] if obi_id not in parent_to_children else parent_to_children[obi_id]
        term['source'] = { 'display_name': 'OBI Consortium'}
        obi_id = obi_id.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=OBI&iri=http://purl.obolibrary.org/obo/' + obi_id,
                         'source': {'display_name': 'OBO Foundry'},
                         'url_type': 'Ontobee'}]
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, obinvestigation_starter, 'obinvestigation', lambda x: x['display_name'])




