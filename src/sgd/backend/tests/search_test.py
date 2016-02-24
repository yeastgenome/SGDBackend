import json
import pytest
import requests

BASE_URL = 'http://0.0.0.0:6543/'
SEARCH_URL = BASE_URL + 'get_search_results'

def query_search(query):
	url = SEARCH_URL +'?q=' + query
	response = requests.get(url).json()
	return response

# SEARCH RESULTS
# search "rad54", get rad54 LSP as top result
response = query_search('rad54')
assert response['results'][0]['href'] == '/locus/S000003131/overview'
# search for ATG, get less than 40 locus results, maybe should be another number
response = query_search('ATG')
aggs = response['aggregations']
for agg in aggs:
	if agg['name'] == 'locus':
		assert agg['total'] < 40
# search BLAST, BLAST should be top result
response = query_search('blast')
assert response['results'][0]['href'] == 'http://yeastgenome.org/blast-sgd'
# search variant viewer, vv should be top result
response = query_search('variant viewer')
assert response['results'][0]['href'] == 'http://www.yeastgenome.org/variant-viewer'
# search for "kinase," see some gene results (but less than 200)
response = query_search('kinase')
aggs = response['aggregations']
for agg in aggs:
	has_locus = False
	if agg['name'] == 'locus':
		has_locus = True
		assert agg['total' < 200]
		assert agg['total' > 100]
assert has_locus

# secondary filter params for loci
# category locus should have aggregations for feature type, phenotype, cellular component, biological process, and molecular function
response = query_search('kinase&category=locus')
# search locus category with blank query and feature type "telomere", all results should be TELXXX-y
response = query_search('&category=locus&feature%20type=telomere')
# search by phenotype, search locus category for query "ADH," and phenotype "UV resistance: decreased," ADH1 should be only result
response = query_search('ADH&category=locus&fphenotype=UV%20resistance%3A%20decreased')
# search by cellular component, search locus cat for query "REP" and cellular component "nucleus," only results should be REP1, and REP2
response = query_search('REP&category=locus&cellular%20component=nucleus')
