from src.sgd.convert.into_curate import basic_convert, remove_nones
from sqlalchemy.sql.expression import or_

__author__ = 'kpaskov'

key_switch = {'id': 'chebi_id', 'name': 'name', 'def': 'description', 'created_by': 'created'}

def chemical_starter(bud_session_maker):
    from src.sgd.model.bud.cv import CVTerm
    from src.sgd.model.bud.phenotype import ExperimentProperty

    bud_session = bud_session_maker()

    chebi_to_date_created = {}
    for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no == 3).all():
        if bud_obj.dbxref_id is not None:
            chebi_to_date_created[bud_obj.dbxref_id] = (str(bud_obj.date_created), bud_obj.created_by)
        else:
            yield remove_nones({'name': bud_obj.name,
                                'source': {'name': 'SGD'},
                                'bud_id': bud_obj.id,
                                'description': bud_obj.definition,
                                'date_created': str(bud_obj.date_created),
                                'created_by': bud_obj.created_by})

    for bud_obj in bud_session.query(ExperimentProperty).filter(or_(ExperimentProperty.type=='Chemical_pending', ExperimentProperty.type == 'chebi_ontology')).all():
        yield {'name': bud_obj.value,
               'bud_id': bud_obj.id,
               'source': {'name': 'SGD'},
               'date_created': str(bud_obj.date_created),
               'created_by': bud_obj.created_by}

    terms = []
    parent_to_children = dict()
    f = open('src/sgd/convert/data/chebi.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'name': 'EBI'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    name = quotation_split[1]
                    alias_type = quotation_split[2].split('[')[0].strip()[:40]
                    if len(name) < 500 and (name, alias_type) not in [(x['name'], x['alias_type']) for x in term['aliases']]:
                        term['aliases'].append({'name': name, "alias_type": alias_type, "source": {"name": "EBI"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'chebi_id': term['chebi_id'], 'name': term['name'], 'source': {'name': 'EBI'}, 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                else:
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        chebi_id = term['chebi_id']
        term['children'] = [] if chebi_id not in parent_to_children else parent_to_children[chebi_id]
        term['urls'].append({'name': 'EBI',
                              'link': 'http://www.ebi.ac.uk/chebi/searchId.do?chebiId=' + term['chebi_id'],
                              'source': {'name': 'EBI'},
                              'url_type': 'External'})

        if chebi_id in chebi_to_date_created:
            term['date_created'], term['created_by'] = chebi_to_date_created[chebi_id]
        yield term

    bud_session.close()

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, chemical_starter, 'chemical', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

