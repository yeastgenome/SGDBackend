# -*- coding: utf-8 -*-

import unittest
import requests
import re
import pickle
import os
import json

testing_routes = [
    {"name": "chemical", "route": "/chemical/{identifier}/overview", "param": "36294"},
    {"name": "strain", "route": "/strain/{identifier}/overview", "param": "5"},
    {"name": "reference", "route": "/reference/{identifier}/overview", "param": "233"},
    {"name": "experiment", "route": "/experiment/{identifier}/overview", "param": "263"},
    {"name": "reference_list", "route": "/reference_list", "param": "", "payload": '{"reference_ids":[1, 2]}'},
    {"name": "go_enrichment", "route": "/go_enrichment", "param": "", "payload": '{"bioent_ids":[1, 2]}'},
    {"name": "bioentity_list", "route": "/bioentity_list", "param": "", "payload": '{"bioent_ids":[1, 2]}'},
    {"name": "alignment_bioent", "route": "/alignments/{identifier}", "param": "1020"},
    {"name": "author", "route": "/author/{identifier}/overview", "param": "233"},
    {"name": "references_this_week", "route": "/references/this_week", "param": ""},
    {"name": "locus", "route": "/locus/{identifier}/overview", "param": "233"},
    {"name": "locustabs", "route": "/locus/{identifier}/tabs", "param": "233"},
    {"name": "go", "route": "/go/{identifier}/overview", "param": "12627"},
    {"name": "go_bioent_details", "route": "/locus/{identifier}/go_details", "param": "233"},
    {"name": "go_biocon_details", "route": "/go/{identifier}/locus_details", "param": "12627"},
    {"name": "go_biocon_details_all", "route": "/go/{identifier}/locus_details_all", "param": "12627"},
    {"name": "go_ref_details", "route": "/reference/{identifier}/go_details", "param": "12627"},
    {"name": "go_graph", "route": "/locus/{identifier}/go_graph", "param": "233"},
    {"name": "go_ontology_graph", "route": "/go/{identifier}/ontology_graph", "param": "12627"},
    {"name": "expression_details", "route": "/locus/{identifier}/expression_details", "param": "233"},
    {"name": "expression_graph", "route": "/locus/{identifier}/expression_graph", "param": "233"},
    {"name": "phenotype", "route": "/phenotype/{identifier}/overview", "param": "46027"},
    {"name": "observable", "route": "/observable/{identifier}/overview", "param": "43803"},
    {"name": "phenotype_bioent_details", "route": "/locus/{identifier}/phenotype_details", "param": "233"},
    {"name": "phenotype_biocon_details", "route": "/phenotype/{identifier}/locus_details", "param": "46027"},
    {"name": "phenotype_obs_details", "route": "/observable/{identifier}/locus_details", "param": "43854"},
    {"name": "phenotype_obs_details_all", "route": "/observable/{identifier}/locus_details_all", "param": "43854"},
    {"name": "phenotype_chem_details", "route": "/chemical/{identifier}/phenotype_details", "param": "50011"},
    {"name": "phenotype_ref_details", "route": "/reference/{identifier}/phenotype_details", "param": "94544"},
    {"name": "phenotype_graph", "route": "/locus/{identifier}/phenotype_graph", "param": "233"},
    {"name": "phenotype_ontology_graph", "route": "/observable/{identifier}/ontology_graph", "param": "43854"},
    {"name": "interaction_bioent_details", "route": "/locus/{identifier}/interaction_details", "param": "233"},
    {"name": "interaction_ref_details", "route": "/reference/{identifier}/interaction_details", "param": "94544"},
    {"name": "interaction_graph", "route": "/locus/{identifier}/interaction_graph", "param": "233"},
    {"name": "regulation_bioent_details", "route": "/locus/{identifier}/regulation_details", "param": "233"},
    {"name": "regulation_ref_details", "route": "/reference/{identifier}/regulation_details", "param": "94544"},
    {"name": "regulation_target_enrichment", "route": "/locus/{identifier}/regulation_target_enrichment", "param": "233"},
    {"name": "regulation_graph", "route": "/locus/{identifier}/regulation_graph", "param": "233"},
    {"name": "literature_bioent_details", "route": "/locus/{identifier}/literature_details", "param": "233"},
    {"name": "literature_ref_details", "route": "/reference/{identifier}/literature_details", "param": "94544"},
    {"name": "literature_topic_details", "route": "/topic/{identifier}/literature_details", "param": "1706"},
    {"name": "literature_graph", "route": "/locus/{identifier}/literature_graph", "param": "233"},
    {"name": "protein_domain_bioent_details", "route": "/locus/{identifier}/protein_domain_details", "param": "233"},
    {"name": "protein_domain_bioitem_details", "route": "/domain/{identifier}/locus_details", "param": "10198"},
    {"name": "domain", "route": "/domain/{identifier}/overview", "param": "10198"},
    {"name": "domain_enrichment", "route": "/domain/{identifier}/enrichment", "param": "10198"},
    {"name": "protein_domain_graph", "route": "/locus/{identifier}/protein_domain_graph", "param": "233"},
    {"name": "binding_site_bioent_details", "route": "/locus/{identifier}/binding_site_details", "param": "233"},
    {"name": "ecnumber", "route": "/ecnumber/{identifier}/overview", "param": "1623808"},
    {"name": "ecnumber_bioent_details", "route": "/locus/{identifier}/ecnumber_details", "param": "233"},
    {"name": "ecnumber_biocon_details", "route": "/ecnumber/{identifier}/locus_details", "param": "1623808"},
    {"name": "sequence_bioent_details", "route": "/locus/{identifier}/sequence_details", "param": "233"},
    {"name": "sequence_contig_details", "route": "/contig/{identifier}/sequence_details", "param": "230728"},
    {"name": "sequence_neighbor_details", "route": "/locus/{identifier}/neighbor_sequence_details", "param": "233"},
    {"name": "protein_phosphorylation_details", "route": "/locus/{identifier}/protein_phosphorylation_details", "param": "233"},
    {"name": "protein_experiment_details", "route": "/locus/{identifier}/protein_experiment_details", "param": "233"},
    {"name": "contig", "route": "/contig/{identifier}/overview", "param": "230728"},
    {"name": "dataset", "route": "/dataset/{identifier}/overview", "param": "258996"},
    {"name": "tag", "route": "/tag/{identifier}/overview", "param": "22"},
    {"name": "tag_list", "route": "/tag", "param": ""},
    {"name": "locus_list", "route": "/locus/{identifier}", "param": "ORF"},
    {"name": "snapshot", "route": "/snapshot", "param": ""},
    {"name": "alignments", "route": "/alignments", "param": ""},
    {"name": "reserved_name", "route": "/reserved_name/{identifier}/overview", "param": "200424"},
    {"name": "posttranslational_details", "route": "/locus/{identifier}/posttranslational_details", "param": "233"}
]

RESPONSES_FILE = "responses.pickle"

class TestEndpoints(unittest.TestCase):
    def executeRequests(self, test, setup):
        setup["requests"] = {}
        
        for attempt in range(5):
            try:
                if test.get("payload"):
                    for url in setup["urls"]:
                        setup["requests"][url] = requests.post(setup["urls"][url], data = test.get("payload"))
                else:
                    for url in setup["urls"]:
                        setup["requests"][url] = requests.get(setup["urls"][url])
            except:
                print "Retrying..."
            else:
                break

        for r in setup["requests"]:
            url = setup["requests"][r].url
            status_code = setup["requests"][r].status_code

            if status_code != 200:
                self.status_500.append(url)
                continue
            else:
                self.assertEqual(status_code, 200, url)
                
            text = setup["requests"][r].text
            rjson = json.loads(text) if text != "" else {}
            
            if self.responses.get(url):
                self.assertEqual(rjson, self.responses[url])
            else:
                self.responses[url] = rjson
    
    def testSingleEndpoint(self):
        self.status_500 = []

        for test in testing_routes:
            setup = {}
            setup["urls"] = {}

            setup["urls"][os.environ["HOST"]] = os.environ["HOST"] + re.sub("\{identifier\}", test["param"], test["route"])

            print " <~> ".join([setup["urls"][h] for h in setup["urls"]])

            self.executeRequests(test, setup)

        if len(self.status_500) > 0:
            print "\nALERT: The following endpoints are broken (500):"
            for url in self.status_500:
                print url

    def testCompares(self):
        self.status_500 = []

        for test in testing_routes:
            setup = {}
            setup["urls"] = {}

            for h in [os.environ["HOST_1"], os.environ["HOST_2"]]:
                setup["urls"][h] = h + re.sub("\{identifier\}", test["param"], test["route"])

            print " <~> ".join([setup["urls"][h] for h in setup["urls"]])

            self.executeRequests(test, setup)
            
            keys = setup["requests"].keys()
            for i in xrange(len(keys)):
                for j in xrange(i, len(keys)):
                    r_1 = setup["requests"][keys[i]]
                    r_2 = setup["requests"][keys[j]]
                    if r_1.status_code == 200 and r_2.status_code == 200:
                        self.assertEqual(json.loads(r_1.text) if r_1.text != "" else {}, json.loads(r_2.text) if r_2.text != "" else {})
                
        if len(self.status_500) > 0:
            print "\nALERT: The following endpoints are broken (500):"
            for url in self.status_500:
                print url
                
    def setUp(self):
        if os.path.isfile(RESPONSES_FILE):
            self.responses = pickle.load(open(RESPONSES_FILE, "rb"))
        else:
            self.responses = {}
        
    def tearDown(self):
        with open(RESPONSES_FILE, "wb") as f:
            pickle.dump(self.responses, f)

if __name__ == '__main__':
    unittest.main()
