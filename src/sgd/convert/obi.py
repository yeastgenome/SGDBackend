from src.sgd.convert import basic_convert
from src.sgd.convert.util import read_obo

__author__ = 'sweng66'

key_switch = {'id': 'obiid', 'name': 'display_name', 'def': 'description'}

def obi_starter(bud_session_maker):
    
    parent_to_children = dict()
    is_obsolete_id = dict()
    source = 'OBI Consortium'
    ## http://www.berkeleybop.org/ontologies/obi.obo
    terms = read_obo('OBI', 
                     'src/sgd/convert/data/obi.obo', 
                     key_switch,
                     parent_to_children,
                     is_obsolete_id,
                     source)

    for term in terms:
        if term.get('obiid') == None or term.get('display_name') == None:
            continue
        obiid = term['obiid']
        if obiid in is_obsolete_id:
            continue
        print obiid
        if obiid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[obiid]:
                child_id = child['obiid']
                if child_id not in is_obsolete_id:
                    children.append(child)
            term['children'] = children
        term['source'] = { 'display_name': 'OBI Consortium'}
        obiid = obiid.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=OBI&iri=http://purl.obolibrary.org/obo/' + obiid,
                         'source': {'display_name': 'OBO Foundry'},
                         'url_type': 'Ontobee'}]
        yield term

    ## add NTR terms:                                                                                        
    files = ['src/sgd/convert/data/published_datasets_metadata_dataset-20160804.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_dataset_OWL.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_dataset-OWL.txt',
             'src/sgd/convert/data/non-GEO-dataset.tsv']

    found = {}
    i = 0
    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip()
            if line:
                pieces = line.split("\t")
                if len(pieces) > 7:
                    if pieces[7].startswith('NTR:'):
                        display_name = pieces[7].replace('NTR:', '')
                        if display_name not in found:
                            i = i + 1
                            found[display_name] = 1
                            yield { 'source': { 'display_name': 'SGD' },
                                    'obiid': 'NTR:' + str(i),
                                    'format_name': 'NTR:' + str(i),
                                    'display_name': display_name }
     
    for display_name in ['ChIP-exo',
                         'DNA sequence variation detection by snp array',
                         'DNA sequence variation detection by tiling array',
                         'Prediction',
                         'Serial analysis of gene expression',
                         'competitive growth assay analysis with microarrays',
                         'fluorescence detection assay',
                         'synthetic lethality analysis with microarrays',
                         'sequencing']

        if display_name not in found:
            i = i + 1
            found[display_name] = 1
            yield { 'source': { 'display_name': 'SGD' },
                    'obiid': 'NTR:' + str(i),
                    'format_name': 'NTR:' + str(i),
                    'display_name': display_name }

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, obi_starter, 'obi', lambda x: x['display_name'])




