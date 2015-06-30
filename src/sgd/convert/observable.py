from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'

chemical_phenotypes = {'chemical compound accumulation': 'APO:0000095', 'chemical compound excretion': 'APO:0000222', 'resistance to chemicals': 'APO:0000087'}
key_switch = {'id': 'apo_id', 'name': 'display_name', 'def': 'description', 'created_by': 'created'}

def observable_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import Phenotype, PhenotypeFeature

    terms = []
    parent_to_children = dict()
    f = open('src/sgd/convert/data/ascomycete_phenotype.obo', 'r')
    term = None
    for line in f:
        line = line.strip()
        if line == '[Term]':
            if term is not None:
                terms.append(term)
            term = {'aliases': [],
                    'source': {'display_name': 'SGD'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    display_name = quotation_split[1]
                    alias_type = quotation_split[2].split('[')[0].strip()
                    if len(display_name) < 500 and (display_name, alias_type) not in [(x['display_name'], x['alias_type']) for x in term['aliases']]:
                        term['aliases'].append({'display_name': display_name, "alias_type": alias_type, "source": {"display_name": "SGD"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'apo_id': term['apo_id'], 'source': {'display_name': 'SGD'}, 'display_name': term['display_name'], 'relation_type': 'is_a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                else:
                    term[pieces[0]] = pieces[1]
    f.close()

    #Pull observable_type
    top_level = parent_to_children['APO:0000017']
    apo_id_to_observable_type = dict()

    def recurse_through_tree(apo_id, observable_type):
        if apo_id in parent_to_children:
            for child in parent_to_children[apo_id]:
                apo_id_to_observable_type[child['apo_id']] = observable_type
                recurse_through_tree(child['apo_id'], observable_type)

    for observable in top_level:
        apo_id_to_observable_type[observable['apo_id']] = observable['display_name']
        recurse_through_tree(observable['apo_id'], observable['display_name'])

    for term in terms:
        if term['namespace'] == 'observable':
            apo_id = term['apo_id']
            print apo_id
            term['children'] = [] if apo_id not in parent_to_children else parent_to_children[apo_id]

            if term['display_name'] == 'observable':
                term['description'] = 'Features of Saccharomyces cerevisiae cells, cultures, or colonies that can be detected, observed, measured, or monitored.'
                term['display_name'] = 'Yeast Phenotype Ontology'
                term['format_name'] = 'ypo'
            if term['apo_id'] in apo_id_to_observable_type:
                term['observable_type'] = apo_id_to_observable_type[term['apo_id']]
            yield term

    #Chemical Observables
    bud_session = bud_session_maker()
    for bud_obj in bud_session.query(PhenotypeFeature).join(PhenotypeFeature.phenotype).filter(Phenotype.observable.in_(chemical_phenotypes.keys())).all():
        if bud_obj.experiment is not None:
            chemicals = bud_obj.experiment.chemicals
            if len(chemicals) > 0:
                chemical = ' and '.join([x[0] for x in chemicals])
                obj_json = None
                old_observable = bud_obj.phenotype.observable
                if old_observable == 'resistance to chemicals':
                    new_observable = bud_obj.phenotype.observable.replace('chemicals', chemical)
                    obj_json = {'source': {'display_name': 'SGD'},
                                'description': 'The level of resistance to exposure to ' + chemical + '.',
                                'display_name': new_observable}
                elif old_observable == 'chemical compound accumulation':
                    new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                    obj_json = {'source': {'display_name': 'SGD'},
                                'description': 'The production and/or storage of ' + chemical + '.',
                                'display_name': new_observable}
                elif old_observable == 'chemical compound excretion':
                    new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                    obj_json = {'source': {'display_name': 'SGD'},
                                'description': 'The excretion from the cell of ' + chemical + '.',
                                'display_name': new_observable}

                if obj_json is not None:
                    obj_json['observable_type'] = apo_id_to_observable_type[chemical_phenotypes[old_observable]]
                    yield obj_json
    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, observable_starter, 'observable', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
