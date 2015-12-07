# Search API Documentation

This is a specification of desired behavior for the HTTP search API.

## search results

#### request

url: GET `/get_search_results`

parameters

* `q`, string, the query from the user, optional and defaults to empty string.
* `categories`, string, comma-separated list of included facets.  Optional If omitted, returns all categories.  
* `limit`, integer, number of entries to include in each response.  Optional and defaults to 10.
* `offset`, integer, of the total results, where to start getting the results.  Optional and defaults to 0.
 
example: `/get_search_results?q=actin&categories=locus,phenotype&limit=10&offset=30`

#### response

the response object includes the following fields

* `total` integer, total results
* `results` array of objects, each with following fields
   * `name`, string, required
   * `category`, string, required
   * `href`, string, may be null for entried with category "download"
   * `description`, string, may be null
   * `download_metadata`, object, only present for downloads, and omitted otherwise, contains the following fields
      * `title`, string
      * `citation`, string
      * `experiment_type`, array of strings
      * `summary`, string
      * `keywords`, array of strings
      * `pubmed_ids`, array of string
      * `sample_ids`, array of strings
      * `download_url`, string, required, 
* `aggregations` array of objects, each with the following fields
    * `total`, required integers
    * `name`, required string

example response
```json
{  
   "total":1206,
   "results":[  
      {  
         "category":"locus",
         "href":"/locus/S000003826/overview",
         "description":"Essential component of the Arp2/3 complex",
         "name":"ARP3 / YJR065C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000002187/overview",
         "description":"Essential component of the Arp2/3 complex",
         "name":"ARP2 / YDL029W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001855/overview",
         "description":"Actin",
         "name":"ACT1 / YFL039C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000003312/overview",
         "description":"Twinfilin",
         "name":"TWF1 / YGR080W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005707/overview",
         "description":"Actin assembly factor",
         "name":"LAS17 / YOR181W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005648/overview",
         "description":"Profilin",
         "name":"PFY1 / YOR122C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001421/overview",
         "description":"Formin",
         "name":"BNR1 / YIL159W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000002536/overview",
         "description":"Fimbrin, actin-bundling protein",
         "name":"SAC6 / YDR129C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005856/overview",
         "description":"Protein required for normal actin organization and endocytosis",
         "name":"SCD5 / YOR329C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001058/overview",
         "description":"Actin-binding protein",
         "name":"YSC84 / YHR016C"
      }
   ],
   "aggregations":[  
      {  
         "total":817,
         "name":"reference"
      },
      {  
         "total":299,
         "name":"locus"
      },
      {  
         "total":42,
         "name":"biological_process"
      },
      {  
         "total":34,
         "name":"cellular_component"
      },
      {  
         "total":12,
         "name":"molecular_function"
      },
      {  
         "total":2,
         "name":"phenotype"
      }
   ]
}
```

## autocomplete results

#### request

url: GET `/autocomplete_results`

parameters

* `q`, string, the query from the user, optional and defaults to empty string.

#### response

the response object includes the following fields

* `results` array of objects, each with the following fields
    * `name`, string, required
    * `category`, string, optional
    * `href`, string, optional and present for results where users can go directly

example response

```json
{  
   "results":[  
      {  
         "category":"suggestion",
         "name":"ACTin"
      },
      {  
         "href":"/go/GO:0019211/overview",
         "category":"GO",
         "name":"phosphatase activator activity"
      },
      {  
         "href":"/go/GO:0044692/overview",
         "category":"GO",
         "name":"exoribonuclease activator activity"
      },
      {  
         "href":"/go/GO:0005096/overview",
         "category":"GO",
         "name":"GTPase activator activity"
      },
      {  
         "href":"/go/GO:0008047/overview",
         "category":"GO",
         "name":"enzyme activator activity"
      },
      {  
         "href":"/go/GO:0016504/overview",
         "category":"GO",
         "name":"peptidase activator activity"
      },
      {  
         "href":"/go/GO:0001671/overview",
         "category":"GO",
         "name":"ATPase activator activity"
      },
      {  
         "href":"/go/GO:0019781/overview",
         "category":"GO",
         "name":"NEDD8 activating enzyme activity"
      },
      {  
         "href":"/go/GO:0035800/overview",
         "category":"GO",
         "name":"deubiquitinase activator activity"
      }
   ]
}
```
