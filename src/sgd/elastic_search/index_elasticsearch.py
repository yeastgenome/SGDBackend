import os
from elasticsearch import Elasticsearch
import requests

ALIGNMENT_URL = 'http://yeastgenome.org/webservice/alignments'
DEFAULT_ES_ADDRESS = 'http://localhost:9200'
DOC_TYPE = 'searchableItem'
INDEX_NAME = 'search-dev1'
IS_HARD_UPDATE = True

ES_ADDRESS = DEFAULT_ES_ADDRESS
es = Elasticsearch(ES_ADDRESS)

def set_filters():
	new_settings = {
		"analysis": {
			"filter": {
				"autocomplete_filter": { 
					"type":     "edge_ngram",
					"min_gram": 1,
					"max_gram": 20
				}
			},
			"analyzer": {
				"autocomplete": {
					"type":      "custom",
					"tokenizer": "standard",
					"filter": [
						"lowercase",
						"autocomplete_filter" 
					]
				},
				"raw": {
					"type": "custom",
					"tokenizer": "keyword",
					"filter": [
						"lowercase"
					]
				}
			}

		}
	}
	# add autocomplete setting, needs to close and reopen
	es.indices.close(index=INDEX_NAME)
	es.indices.put_settings(index=INDEX_NAME, body=new_settings)
	es.indices.open(index=INDEX_NAME)

def set_mapping():
	mapping_settings = {
		DOC_TYPE: {
			"properties": {
				"name": {
					"type": "string",
					"analyzer": "autocomplete",
					"fields": {
						"raw": {
							"type": "string",
							"analyzer": "raw"
						}
					}
				}
			}
		}
	}
	# drop index and re-create
	es.indices.delete(index=INDEX_NAME, ignore=404)
	es.indices.create(index=INDEX_NAME)
	es.cluster.health(wait_for_status='yellow', request_timeout=5)
	set_filters()
	es.indices.put_mapping(index=INDEX_NAME, doc_type=DOC_TYPE, body=mapping_settings)

def index_loci():
	# get list of genes from alignment webservice
	print '*** FETCHING ALL LOCI ***'
	raw_alignment_data = requests.get(ALIGNMENT_URL).json()
	loci = raw_alignment_data['loci']

	# index loci
	print '*** INDEXING ALL LOCI ***'
	i = 0
	for locus in loci:
		if locus['display_name'] == locus['format_name']:
			name = locus['display_name']
		else:
			name = str(locus['display_name']) + ' / ' + str(locus['format_name'])
		body = {
			'sgdid': locus['sgdid'],
			'name': name,
			'category': 'locus',
			'url': locus['link'],
			'description': locus['headline']
		}
		
		es.index(index=INDEX_NAME, doc_type=DOC_TYPE, id=i, body=body)
		i += 1

def main():
	if IS_HARD_UPDATE:
		set_mapping()
	index_loci()

main()
