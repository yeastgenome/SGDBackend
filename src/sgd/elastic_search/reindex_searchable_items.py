from elasticsearch import helpers
from elasticsearch import Elasticsearch

CLIENT_ADDRESS = 'http://localhost:9200'
INDEX_NAME = 'searchable_items5' # TEMP
DOC_TYPE = 'searchable_item'

RESET_INDEX = False

es = Elasticsearch(CLIENT_ADDRESS)

def reindex():
	# create temp index
	TEMP_INDEX = INDEX_NAME + 'temp_reindex'
	exists = es.indices.exists(TEMP_INDEX)
	if not exists:
		es.indices.create(TEMP_INDEX)
    # transfer to temp index
	helpers.reindex(client=es, source_index=INDEX_NAME, target_index=TEMP_INDEX, target_client=es)
	# transfer back
	helpers.reindex(client=es, source_index=TEMP_INDEX, target_index=INDEX_NAME, target_client=es)
	# delete temp
	es.indices.delete(TEMP_INDEX)

def main():
	reindex()

main()
