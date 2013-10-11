'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment import query_batter
from sgdbackend_utils.cache import get_cached_biocon

'''
-------------------------------Enrichment---------------------------------------
''' 
def make_enrichment(bioent_format_names):
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        goterm = get_cached_biocon(str(int(enrichment_result[0][3:])), 'GO')
        json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
    return json_format
