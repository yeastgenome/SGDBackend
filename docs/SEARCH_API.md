# Search API Documentation

This is a specification of desired behavior for the HTTP search API.

======

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
`name`, string, required
    * `category`, string, required
    * `href`, string, may be null for entried with category "download"
    * `description`, string, may be null
    * `download_metadata`, object, only present for downloads, and omitted otherwise, contains the following fields
        * `pubmed_ids`, array of strings
        * `geo_ids`, array of strings
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
      },
      {  
         "category":"locus",
         "href":"/locus/S000004311/overview",
         "description":"Actin- and formin-interacting protein",
         "name":"BUD6 / YLR319C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001171/overview",
         "description":"Actin-related protein of the dynactin complex",
         "name":"ARP1 / YHR129C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005894/overview",
         "description":"Component of yeast cortical actin cytoskeleton",
         "name":"SCP1 / YOR367W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001296/overview",
         "description":"Beta subunit of the capping protein heterodimer (Cap1p and Cap2p)",
         "name":"CAP2 / YIL034C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000003557/overview",
         "description":"Protein possibly involved in assembly of actin patches",
         "name":"BBC1 / YJL020C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000004075/overview",
         "description":"Actin-related protein that binds nucleosomes",
         "name":"ARP6 / YLR085C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000003368/overview",
         "description":"Negative regulator of actin nucleation-promoting factor activity",
         "name":"LSB1 / YGR136W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005023/overview",
         "description":"Major isoform of tropomyosin",
         "name":"TPM1 / YNL079C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000004329/overview",
         "description":"Verprolin, proline-rich actin-associated protein",
         "name":"VRP1 / YLR337C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000003477/overview",
         "description":"Protein required for actin organization and passage through Start",
         "name":"SDA1 / YGR245C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001490/overview",
         "description":"Alpha subunit of the capping protein heterodimer (Cap1p and Cap2p)",
         "name":"CAP1 / YKL007W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000004421/overview",
         "description":"Coronin",
         "name":"CRN1 / YLR429W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005004/overview",
         "description":"Nuclear actin-related protein involved in chromatin remodeling",
         "name":"ARP5 / YNL059C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005667/overview",
         "description":"Nuclear actin-related protein involved in chromatin remodeling",
         "name":"ARP8 / YOR141C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005765/overview",
         "description":"AdoMet-dependent tRNA methyltransferase and actin binding protein",
         "name":"ABP140 / YOR239W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000002796/overview",
         "description":"Actin-associated protein with roles in endocytosis and exocytosis",
         "name":"RVS167 / YDR388W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000001367/overview",
         "description":"Phosphoinositide PI4,5P(2) binding protein, forms a complex with Slm2p",
         "name":"SLM1 / YIL105C"
      },
      {  
         "category":"locus",
         "href":"/locus/S000004196/overview",
         "description":"Epsin-like protein required for endocytosis and actin patch assembly",
         "name":"ENT2 / YLR206W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000005187/overview",
         "description":"Adaptor protein that links actin to clathrin and endocytosis",
         "name":"SLA2 / YNL243W"
      },
      {  
         "category":"locus",
         "href":"/locus/S000000539/overview",
         "description":"Protein of unknown function",
         "name":"LSB5 / YCL034W"
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


