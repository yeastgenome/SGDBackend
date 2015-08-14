from src.sgd.convert import basic_convert, remove_nones
from src.sgd.convert.util import get_relation_to_ro_id
from sqlalchemy.sql.expression import or_

__author__ = 'sweng66'

key_switch = {'id': 'chebiid', 'name': 'display_name', 'def': 'description'}

def chebi_starter(bud_session_maker):
    
    from src.sgd.model.bud.cv import CVTerm
    from src.sgd.model.bud.phenotype import ExperimentProperty

    bud_session = bud_session_maker()

    chebi_to_date_created = {}
    # for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no == 3).all():
    #    if bud_obj.dbxref_id is not None:
    #        chebi_to_date_created[bud_obj.dbxref_id] = (str(bud_obj.date_created), bud_obj.created_by)
    #    else:
    #        yield remove_nones({'display_name': bud_obj.name,
    #                            'source': {'display_name': 'SGD'},
    #                            'bud_id': bud_obj.id,
    #                            'description': bud_obj.definition,
    #                            'date_created': str(bud_obj.date_created),
    #                            'created_by': bud_obj.created_by})

    # for bud_obj in bud_session.query(ExperimentProperty).filter(or_(ExperimentProperty.type=='Chemical_pending', ExperimentProperty.type == 'chebi_ontology')).all():
    #    yield {'display_name': bud_obj.value,
    #           'bud_id': bud_obj.id,
    #           'source': {'display_name': 'SGD'},
    #           'date_created': str(bud_obj.date_created),
    #           'created_by': bud_obj.created_by}
    
    terms = []
    parent_to_children = dict()
    # downloaded from ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo
    f = open('src/sgd/convert/data/chebi.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'EBI'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    display_name = quotation_split[1]
                    alias_type = quotation_split[2].split('[')[0].strip()[:40]
                    ### 
                    if alias_type not in ('EXACT', 'RELATED', 'EXACT IUPAC_NAME'):
                        continue
                    if alias_type == 'EXACT IUPAC_NAME':
                        alias_type = 'IUPAC name'
                    if len(display_name) < 500 and (display_name, alias_type) not in [(x['display_name'], x['alias_type']) for x in term['aliases']]:
                        term['aliases'].append({'display_name': display_name, "alias_type": alias_type, "source": {"display_name": "EBI"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'chebiid': term['chebiid'], 'display_name': term['display_name'], 'source': {'display_name': 'EBI'}, 'ro_id': get_relation_to_ro_id('is a')})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                else:
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        chebiid = term['chebiid']
        print chebiid
        term['children'] = [] if chebiid not in parent_to_children else parent_to_children[chebiid]
        term['urls'].append({'display_name': 'ChEBI',
                              'link': 'http://www.ebi.ac.uk/chebi/searchId.do?chebiId=' + term['chebiid'],
                              'source': {'display_name': 'EBI'},
                              'url_type': 'ChEBI'})
        yield term

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, chebi_starter, 'chebi', lambda x: x['display_name'])


