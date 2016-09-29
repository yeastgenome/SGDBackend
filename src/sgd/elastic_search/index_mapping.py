mapping = {
    "settings": {
        "index": {
            "max_result_window": 15000,
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard",
                        "filter": ["english_stemmer", "lowercase"]
                    },
                    'simple': {
                        "type": "standard",
                        "filter": ["lowercase"]
                    },
                    "my_analyzer": {
                        "tokenizer": "standard",
                        "filter": ["standard", "english_stemmer", "word_split", "lowercase"]
                    },
                    "autocomplete": {
                        "type": "custom",
                        "filter": ["lowercase", "autocomplete_filter"],
                        "tokenizer": "standard"
                    },
                    "raw": {
                        "type": "custom",
                        "filter": ["lowercase"],
                        "tokenizer": "keyword"
                    }
                },
                "filter": {
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "autocomplete_filter": {
                        "min_gram": "1",
                        "type": "edge_ngram",
                        "max_gram": "20"
                    },
                    "word_split": {
                        "type": "word_delimiter",
                        "split_on_numerics": "false"
                    }
                }
            },
            "number_of_replicas": "1",
            "number_of_shards": "5"
        }
    },
    "mappings": {
        "searchable_item": {
            "properties": {
                "biological_process": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "category": {
                    "type": "string"
                },
                "observable": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "qualifier": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "references": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "phenotype_loci": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "keys": {
                    "type": "string"
                },
                "secondary_sgdid": {
                    "type": "string"
                },
                "chemical": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "mutant_type": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "go_loci": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "strain": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "author": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "journal": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "year": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "reference_loci": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "ec_number": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "tc_number": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "cellular_component": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "description": {
                    "type": "string"
                },
                "sequence_history": {
                    "type": "string"
                },
                "gene_history": {
                    "type": "string"
                },
                "summary": {
                    "type":"string"
                },
                "feature_type": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "href": {
                    "type": "string"
                },
                "molecular_function": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "name": {
                    "type": "string",
                    "analyzer": "my_analyzer",
                    "fields": {
                        "stemmed": {
                            "type": "string",
                            "analyzer": "my_analyzer"
                        },
                        "simple": {
                            "type": "string",
                            "analyzer": "simple"
                        },
                        "raw": {
                            "type": "string",
                            "analyzer": "raw"
                        },
                        "autocomplete": {
                            "type": "string",
                            "analyzer": "autocomplete"
                        }
                    }
                },
                "go_id": {
                    "type": "string"
                },
                "number_annotations": {
                    "type": "integer"
                },
                "name_description": {
                    "type": "string"
                },
                "synonyms": {
                    "type": "string"
                },
                "phenotypes": {
                    "type": "string"
                },
                "protein": {
                    "type": "string",
                    "fields": {
                        "raw": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                }
            }
        }
    }
}
