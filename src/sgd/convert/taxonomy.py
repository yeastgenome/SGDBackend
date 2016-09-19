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
                taxid = pieces[1].replace("NCBITaxon:", "TAX:")
                term = {'taxid': pieces[1],
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
                    parent = parent.replace("NCBITaxon:", "TAX:")
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    term['taxid'] = term['taxid'].replace("NCBITaxon:", "TAX:")    
                    parent_to_children[parent].append({'taxid': term['taxid'], 'display_name': term['display_name'], 'source': {'display_name': source}, 'rank': rank, 'ro_id': get_relation_to_ro_id('is a')})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    quotation_split = pieces[1].split('"')
                    if pieces[0] == 'def':
                        text = quotation_split[1]
                    term[key_switch[pieces[0]]] = text
                elif pieces[0] == 'property_value' and pieces[1].startswith('has_rank NCBITaxon:'):
                    term['rank'] = pieces[1].replace("has_rank NCBITaxon:", "")
                    # term['rank'] = pieces[1].replace("has_rank ", "")
    f.close()

    print "updating the database"

    for term in terms:
        term['taxid'] = term['taxid'].replace('NCBITaxon:', 'TAX:')
        taxid = term['taxid']    
        print taxid
        if term.get('rank') is None:
            term['rank'] = 'no rank'
        term['children'] = [] if taxid not in parent_to_children else parent_to_children[taxid]
        
        taxid = taxid.replace('TAX:', '')

        term['urls'] = [{"display_name": 'NCBI Taxonomy',
                         "url_type": 'NCBI Taxonomy',
                         "source": {'display_name': source},
                         "link": "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+taxid}]
        yield term

    ## "TAX:562": "Escherichia coli",
    extra_taxid_to_term = { "TAX:4896": "Schizosaccharomyces pombe",
                            "TAX:4931": "Saccharomyces bayanus",
                            "TAX:27291": "Saccharomyces paradoxus",
                            "TAX:4952": "Yarrowia lipolytica",
                            "TAX:5476": "Candida albicans",
                            "TAX:10090": "Mus musculus",
                            "TAX:9606": "Homo sapiens",
                            "TAX:4959": "Debaryomyces hansenii",
                            "TAX:4897": "Schizosaccharomyces japonicus" }

    for taxid in extra_taxid_to_term:
        term = {}
        term['taxid'] = taxid
        term['format_name'] = extra_taxid_to_term[taxid].replace(' ', '_')
        term['display_name'] = extra_taxid_to_term[taxid]
        term['obj_url'] = '/taxonomy/' + term['format_name']
        term['source'] = { 'display_name': 'NCBI' }
        term['rank'] = 'no rank'
        yield term

    index = 100
    for strain in ["BY4742", "D273-10B", "DBVPG6044", "FY1679", "JK9-3d", "K11", "L1528", "SEY6210", "X2180-1A", "YPH499", "YPS128", "YS9", "Y55", "BC187", "UWOPSS", "CENPK"]:
        term = {}
        term['taxid'] = 'NTR:' + str(index)
        term['format_name'] = 'Saccharomyces_cerevisiae_' + strain
        term['display_name'] = 'Saccharomyces cerevisiae ' + strain
        term['obj_url'] = '/taxonomy/' + term['format_name']
        term['source'] = { 'display_name': 'SGD' }
        term['rank'] = 'no rank'
        index = index + 1
        yield term

    


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, taxonomy_starter, 'taxonomy', lambda x: x['display_name'])




