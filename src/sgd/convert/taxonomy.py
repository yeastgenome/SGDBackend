from src.sgd.convert import basic_convert
from src.sgd.convert.util import children_from_obo, get_relation_to_ro_id

__author__ = 'sweng66'

key_switch = {'name': 'display_name', 'def': 'description'}
ancestor = 'NCBITaxon:4893'
source = 'NCBI'

def taxonomy_starter(bud_session_maker):
    
    ## downloaded from http://www.berkeleybop.org/ontologies/ncbitaxon.obo
    f = open('src/sgd/convert/data/ncbitaxon.obo', 'r')
    
    print "getting children of taxon_id=4893"

    [filtered_set, id_to_rank] = children_from_obo('src/sgd/convert/data/ncbitaxon.obo',
                                                   ancestor)

    ## total 1018 in the filtered set
    ## print "COUNT=", len(filtered_set)

    print "reading info for taxon_id 4893 and its children"

    terms = []
    parent_to_children = dict()
    term = None
    for line in f:
        line = line.strip()
        pieces = line.split(': ')
        if line == '[Term]':
            continue
        elif pieces[0] == 'id':
            if term is not None:
                terms.append(term)
                term = None
            if pieces[1] in filtered_set:
                taxid = pieces[1].replace("NCBITaxon:", "")
                term = {'taxid': int(taxid),
                        'aliases': [],
                        'source': {'display_name': source},
                        'urls': []}
        elif term is not None:
            pieces = line.split(': ')
            if len(pieces) == 2:
                if pieces[0] == 'synonym':
                    quotation_split = pieces[1].split('"')
                    if 'EXACT common_name' in quotation_split[2]:
                        term['common_name'] = quotation_split[1]
                    else:
                        alias_type = 'Synonym'
                        if 'common_name' in quotation_split[2]:
                            alias_type = 'Secondary common name'
                        term['aliases'].append({'display_name': quotation_split[1], "alias_type": alias_type, "source": {"display_name": source}})
                elif pieces[0] == 'is_a':
                    parent = pieces[1].split('!')[0].strip()
                    rank = id_to_rank.get(parent)
                    if rank is None:
                        rank = 'no rank'
                    parent = parent.replace("NCBITaxon:", "")
                    parent = int(parent)
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({'taxid': term['taxid'], 'display_name': term['display_name'], 'source': {'display_name': source}, 'rank': rank, 'ro_id': get_relation_to_ro_id('is a')})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                elif pieces[0] == 'property_value' and pieces[1].startswith('has_rank NCBITaxon:'):
                    term['rank'] = pieces[1].replace("has_rank NCBITaxon:", "")
    f.close()

    print "updating the database"

    for term in terms:
        taxid = term['taxid']
        print taxid
        if term.get('rank') is None:
            term['rank'] = 'no rank'
        term['children'] = [] if taxid not in parent_to_children else parent_to_children[taxid]

        term['urls'] = [{"display_name": 'NCBI Taxonomy',
                         "url_type": 'NCBI Taxonomy',
                         "source": {'display_name': source},
                         "link": "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+str(taxid)}]
        yield term


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, taxonomy_starter, 'taxonomy', lambda x: x['display_name'])




