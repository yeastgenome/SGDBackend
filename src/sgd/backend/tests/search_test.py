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
# search for ATG, get 36 locus results
response = query_search('ATG')
aggs = response['aggregations']
for agg in aggs:
	if agg['name'] == 'locus':
		assert agg['total' == 36]
# search BLAST, BLAST should be top result
response = query_search('blast')
assert response['results'][0]['href'] == '/blast-sgd'
# search variant viewer, vv should be top result
response = query_search('variant viewer')
assert response['results'][0]['href'] == 'variant-viewer'
# search for "phosphoprotein phosphatase activity," see less than 100 gene results
response = query_search('phosphoprotein phosphatase activity')
aggs = response['aggregations']
for agg in aggs:
	if agg['name'] == 'locus':
		assert agg['total' < 100]


# AUTOCOMPLETE results

# get ATG genes for q "atg"
# act1 top result for q "act1"
# variant viewer top result for q "variant"
