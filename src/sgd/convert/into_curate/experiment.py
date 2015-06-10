from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'


large_scale_survey = {'large-scale survey', 'competitive growth', 'heterozygous_diploid, large-scale_survey', 'homozygous_diploid, large-scale_survey', 'systematic mutation set', 'heterozygous diploid, competitive growth',
                      'homozygous diploid, competitive growth', 'heterozygous diploid, systematic mutation set', 'homozygous diploid, systematic mutation set'}
classical_genetics = {'classical genetics', 'heterozygous diploid', 'homozygous diploid'}

key_switch = {'id': 'apo_id', 'name': 'name', 'def': 'description', 'created_by': 'created'}

def experiment_starter(bud_session_maker):

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
                    'source': {'name': 'SGD'},
                    'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    name = quotation_split[1]
                    alias_type = quotation_split[2].split('[')[0].strip()
                    if len(name) < 500 and (name, alias_type) not in [(x['name'], x['alias_type']) for x in term['aliases']]:
                        term['aliases'].append({'name': name, "alias_type": alias_type, "source": {"name": "SGD"}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'apo_id': term['apo_id'], 'source': {'name': 'SGD'}, 'name': term['name'], 'relation_type': 'is a'})
                elif pieces[0] in key_switch:
                    term[key_switch[pieces[0]]] = pieces[1]
                else:
                    term[pieces[0]] = pieces[1]
    f.close()

    for term in terms:
        if term['namespace'] == 'experiment_type':
            apo_id = term['apo_id']
            term['children'] = [] if apo_id not in parent_to_children else parent_to_children[apo_id]

            if term['name'] in large_scale_survey:
                term['experiment_type'] = 'large-scale survey'
            if term['name'] in classical_genetics:
                term['experiment_type'] = 'classical genetics'
            yield term


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, experiment_starter, 'experiment', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

