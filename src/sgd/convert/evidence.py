from src.sgd.convert import basic_convert

__author__ = 'kpaskov'
## updated by sweng66

key_switch = {'id': 'eco_id', 'name': 'display_name', 'def': 'description'}

def evidence_starter(bud_session_maker):
    terms = []
    parent_to_children = dict()
    ## downloaded from http://evidenceontology.googlecode.com/svn/trunk/eco.obo
    f = open('src/sgd/convert/data/eco.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'ECO'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    term['aliases'].append({'display_name': quotation_split[1], "alias_type": quotation_split[2].split('[')[0].strip(), "source": {"display_name": "ECO"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'eco_id': term['eco_id'], 'display_name': term['display_name'], 'source': {'display_name': 'ECO'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                elif pieces[0] == 'is_obsolete':
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        if term.get('is_obsolete'):
            continue
        eco_id = term['eco_id']
        print eco_id
        term['children'] = [] if eco_id not in parent_to_children else parent_to_children[eco_id]
        term['urls'].append({'display_name': 'BioPortal',
                              'link': 'http://bioportal.bioontology.org/ontologies/ECO?p=classes&conceptid=' + term['eco_id'],
                              'source': {'display_name': 'BioPortal'},
                              'url_type': 'BioPortal'})
        term['urls'].append({'display_name': 'OLS',
                              'link': 'http://www.ebi.ac.uk/ontology-lookup/?termId=' + term['eco_id'],
                              'source': {'display_name': 'EBI'},
                              'url_type': 'OLS'})
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, evidence_starter, 'evidence', lambda x: x['display_name'])




