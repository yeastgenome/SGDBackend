# -*- coding: utf-8 -*-

import unittest
import requests
import re
import pickle
import os.path
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
    {"name": "history_details", "route": "/locus/{identifier}/history_details", "param": "233"},
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

RESPONSES_FILE = "prod_responses.pickle"
PROD_HOST="http://yeastgenome.org/webservice"
QA_HOST="http://localhost:6543"

class TestEnpoints(unittest.TestCase):

    def testCompares(self):
        status_500 = []
        for test in testing_routes:
            prod_url = PROD_HOST + re.sub("\{identifier\}", test["param"], test["route"])
            qa_url = QA_HOST + re.sub("\{identifier\}", test["param"], test["route"])
            print prod_url + " <~> " + qa_url
            
            for attempt in range(5):
                try:
                    if test.get("payload"):
                        prod_r = requests.post(prod_url, data = test.get("payload"))
                        qa_r = requests.post(qa_url, data = test.get("payload"))
                    else:
                        prod_r = requests.get(prod_url)
                        qa_r = requests.get(qa_url)
                except:
                    print "Retrying..."
                else:
                    break
            
            if prod_r.status_code == 500:
                status_500.append(prod_r.url)
                continue
            else:
                self.assertEqual(prod_r.status_code, 200, prod_r.url)

            if qa_r.status_code == 500:
                status_500.append(qa_r.url)
                continue
            else:
                self.assertEqual(qa_r.status_code, 200, qa_r.url)

            if self.responses.get(test["name"]):
                self.assertEqual(prod_r.json(), self.responses[test["name"]])
            else:
                self.responses[test["name"]] = json.loads(prod_r.text) if prod_r.text != "" else {}

        self.assertEqual(json.loads(prod_r.text) if prod_r.text != "" else {}, json.loads(qa_r.text) if qa_r.text != "" else {})
                
        if len(status_500) > 0:
            print "ALERT: The following endpoints are broken (500):"
            for url in status_500:
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
