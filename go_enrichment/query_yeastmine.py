'''
Created on Sep 27, 2013

@author: kpaskov
'''

from go_enrichment.yeastmine_config import WEB_USER, WEB_PASS
from intermine.webservice import Service

SERVER = "http://yeastmine.yeastgenome.org/yeastmine/service"
GENE_OBJECT = "Gene"


def query_go_processes(bioent_format_names):
    if len(bioent_format_names) > 0:
        service = Service(SERVER, WEB_USER, WEB_PASS)
            
        my_list = service.create_list(set(bioent_format_names), GENE_OBJECT)
        
        enrichment = my_list.calculate_enrichment("go_enrichment_for_gene")
    
        enrichment_results = [(row["identifier"], row["matches"], row['p-value']) for row in enrichment]
        return enrichment_results
    else:
        return []
