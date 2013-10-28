'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment import query_batter
from sgdbackend_query import get_obj_id
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent

'''
-------------------------------Enrichment---------------------------------------
''' 
def make_enrichment(bioent_ids):
    bioent_format_names = [id_to_bioent[bioent_id]['format_name'] for bioent_id in bioent_ids]
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        identifier = enrichment_result[0]
        goterm_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        goterm = id_to_biocon[goterm_id]
        json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
    return json_format
