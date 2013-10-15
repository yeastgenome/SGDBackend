'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment import query_batter
from sgdbackend_query import get_obj_id
from sgdbackend_utils.cache import id_to_biocon

'''
-------------------------------Enrichment---------------------------------------
''' 
def make_enrichment(bioent_format_names):
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        identifier = str(int(enrichment_result[0][3:]))
        goterm_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        if goterm_id is not None:
            goterm = id_to_biocon[goterm_id]
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
    return json_format
