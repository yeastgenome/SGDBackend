'''
Created on Oct 9, 2013

@author: kpaskov
'''
import json
import requests
def get_json(url, data=None):
    print url
    if data is not None:
        headers = {'Content-type': 'application/json; charset=utf-8"', 'processData': False}
        r = requests.post(url, data=json.dumps(data), headers=headers)
    else:
        r = requests.get(url)
    try:
        return r.json()
    except:
        return None

def query_go_processes(bioent_format_names):
    if len(bioent_format_names) > 0:
        enrichment = get_json('http://batter.stanford.edu/cgi-bin/termfinder2.pl', data={"genes":",".join(set(bioent_format_names)),"aspect":"P"})
        enrichment_results = [(row["goid"], row["num_gene_annotated"], row['pvalue']) for row in enrichment]
        return enrichment_results
    else:
        return []