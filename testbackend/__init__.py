from backend.backend_interface import BackendInterface
from datetime import datetime
from go_enrichment import query_batter
from model_perf_schema.bioentity_data import create_data_classes, data_classes
from mpmath import ceil
from perfbackend_utils import set_up_logging
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.response import Response
import json
import sys

class TestBackend(BackendInterface):
    def __init__(self):
        pass
    
    #Renderer
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name, request):
        callback = None if 'callback' not in request.GET else request.GET['callback']
        def f(data):
            if callback is not None:
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        return None
    
    def bioentity_list(self, bioent_ids):
        return None
    
    #Locus
    def locus(self, identifier):
        if identifier == 'ACT1' or identifier == 'YFL039C' or identifier == '4430':
            return json.dumps({
                               'display_name': "ACT1",
                               'class_type': "LOCUS",
                               'format_name': "YFL039C",
                               'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YFL039C",
                               'sgdid': "S000001855",
                               'id': 4430,
                               'description': "Actin; structural protein involved in cell polarization, endocytosis, and other cytoskeletal functions"
                               })
        elif identifier == 'GAL4' or identifier == 'YPL248C' or identifier == '1633':
            return json.dumps({
                               'display_name': "GAL4",
                               'class_type': "LOCUS",
                               'format_name': "YPL248C",
                               'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YPL248C",
                               'sgdid': "S000006169",
                               'id': 1633,
                               'description': "DNA-binding transcription factor required for the activation of the GAL genes in response to galactose; repressed by Gal80p and activated by Gal3p"
                               })
        return None
    
    def locustabs(self, identifier):
        if identifier == 'ACT1' or identifier == 'YFL039C' or identifier == '4430':
            return json.dumps({
                               'protein_tab': True,
                               'interaction_tab': True,
                               'summary_tab': True,
                               'wiki_tab': True,
                               'expression_tab': True,
                               'phenotype_tab': True,
                               'literature_tab': True,
                               'go_tab': True,
                               'regulation_tab': True,
                               'id': 4430,
                               'history_tab': True
                               })
        elif identifier == 'GAL4' or identifier == 'YPL248C' or identifier == '1633':
            return json.dumps({
                               'protein_tab': True,
                               'interaction_tab': True,
                               'summary_tab': True,
                               'wiki_tab': True,
                               'expression_tab': True,
                               'phenotype_tab': True,
                               'literature_tab': True,
                               'go_tab': True,
                               'regulation_tab': True,
                               'id': 1633,
                               'history_tab': True
                               })
        return None
    
    def all_locustabs(self, min_id, max_id):
        return None
    
    #Bioconcept
    def all_bioconcepts(self, min_id, max_id, callback=None):
        return None
    
    def bioconcept_list(self, biocon_ids, callback=None):
        return None
    
    #Reference
    def reference(self, identifier):
        return None
       
    def all_references(self, min_id, max_id):
        return None

    def all_bibentries(self, min_id, max_id):
        return None
    
    def reference_list(self, reference_ids):
        return None
     
    #Go
    def go(self, identifier):
        return None
    
    def go_ontology_graph(self, identifier):
        return None
    
    def go_overview(self, identifier):
        return None
    
    def go_details(self, locus_identifier=None, go_identifier=None):
        return None
    
    #Interaction
    def interaction_overview(self, identifier):
        if identifier == 'ACT1' or identifier == 'YFL039C' or identifier == '4430':
            return json.dumps({
                               'phys_circle_size': 6.6755811781245455,
                               'num_both_interactors': 41,
                               'circle_distance': 15.509187916358625,
                               'num_phys_interactors': 140,
                               'num_gen_interactors': 595,
                               'gen_circle_size': 13.762063154896342
                               })
        elif identifier == 'GAL4' or identifier == 'YPL248C' or identifier == '1633':
            return json.dumps({
                               'phys_circle_size': 4.51351666838205,
                               'num_both_interactors': 10,
                               'circle_distance': 5.130630508378017,
                               'num_phys_interactors': 64,
                               'num_gen_interactors': 32,
                               'gen_circle_size': 3.1915382432114616
                               })
        return None
    
    def interaction_details(self, identifier):
        if identifier == 'ACT1' or identifier == 'YFL039C' or identifier == '4430':
            return json.dumps([
                                {
                                'direction': "Hit",
                                'class_type': "GENINTERACTION",
                                'reference': {
                                'link': "http://www.yeastgenome.org/cgi-bin/reference/reference.pl?dbid=S000126382",
                                'display_name': "Haarer B, et al. (2007)",
                                'id': 63305
                                },
                                'strain': None,
                                'bioentity2': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YBL087C",
                                'display_name': "RPL23A",
                                'id': 1449,
                                'format_name': "YBL087C",
                                'class_type': "LOCUS"
                                },
                                'bioentity1': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YFL039C",
                                'display_name': "ACT1",
                                'id': 4430,
                                'format_name': "YFL039C",
                                'class_type': "LOCUS"
                                },
                                'interaction_type': "Genetic",
                                'note': "these complex haploinsufficient interactions with the act1-null heterozygote are sick",
                                'source': "BioGRID",
                                'experiment': {
                                'link': None,
                                'display_name': "Synthetic Haploinsufficiency",
                                'id': 36
                                },
                                'phenotype': None,
                                'id': 687988,
                                'annotation_type': "high-throughput"
                                },
                                {
                                'direction': "Hit",
                                'class_type': "GENINTERACTION",
                                'reference': {
                                'link': "http://www.yeastgenome.org/cgi-bin/reference/reference.pl?dbid=S000126382",
                                'display_name': "Haarer B, et al. (2007)",
                                'id': 63305
                                },
                                'strain': None,
                                'bioentity2': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YCR094W",
                                'display_name': "CDC50",
                                'id': 1351,
                                'format_name': "YCR094W",
                                'class_type': "LOCUS"
                                },
                                'bioentity1': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YFL039C",
                                'display_name': "ACT1",
                                'id': 4430,
                                'format_name': "YFL039C",
                                'class_type': "LOCUS"
                                },
                                'interaction_type': "Genetic",
                                'note': None,
                                'source': "BioGRID",
                                'experiment': {
                                'link': None,
                                'display_name': "Synthetic Haploinsufficiency",
                                'id': 36
                                },
                                'phenotype': None,
                                'id': 679590,
                                'annotation_type': "high-throughput"
                                }])
        elif identifier == 'GAL4' or identifier == 'YPL248C' or identifier == '1633':
            return json.dumps([
                                {
                                'direction': "Bait",
                                'class_type': "GENINTERACTION",
                                'reference': {
                                'link': "http://www.yeastgenome.org/cgi-bin/reference/reference.pl?dbid=S000120881",
                                'display_name': "Collins SR, et al. (2007)",
                                'id': 57902
                                },
                                'strain': None,
                                'bioentity2': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YPR110C",
                                'display_name': "RPC40",
                                'id': 50,
                                'format_name': "YPR110C",
                                'class_type': "LOCUS"
                                },
                                'bioentity1': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YPL248C",
                                'display_name': "GAL4",
                                'id': 1633,
                                'format_name': "YPL248C",
                                'class_type': "LOCUS"
                                },
                                'interaction_type': "Genetic",
                                'note': "An Epistatic MiniArray Profile (E-MAP) analysis was used to quantitatively score genetic interactions based on fitness defects estimated from the colony size of double versus single mutants. Genetic interactions were considered significant if they had an S score > 2.5 for positive interactions (suppression) and S score < -2.5 for negative interactions (synthetic sick/lethality).",
                                'source': "BioGRID",
                                'experiment': {
                                'link': None,
                                'display_name': "Positive Genetic",
                                'id': 49
                                },
                                'phenotype': None,
                                'id': 568600,
                                'annotation_type': "high-throughput"
                                },
                                {
                                'direction': "Hit",
                                'class_type': "GENINTERACTION",
                                'reference': {
                                'link': "http://www.yeastgenome.org/cgi-bin/reference/reference.pl?dbid=S000120881",
                                'display_name': "Collins SR, et al. (2007)",
                                'id': 57902
                                },
                                'strain': None,
                                'bioentity2': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YGL043W",
                                'display_name': "DST1",
                                'id': 86,
                                'format_name': "YGL043W",
                                'class_type': "LOCUS"
                                },
                                'bioentity1': {
                                'link': "http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=YPL248C",
                                'display_name': "GAL4",
                                'id': 1633,
                                'format_name': "YPL248C",
                                'class_type': "LOCUS"
                                },
                                'interaction_type': "Genetic",
                                'note': "An Epistatic MiniArray Profile (E-MAP) analysis was used to quantitatively score genetic interactions based on fitness defects estimated from the colony size of double versus single mutants. Genetic interactions were considered significant if they had an S score > 2.5 for positive interactions (suppression) and S score < -2.5 for negative interactions (synthetic sick/lethality).",
                                'source': "BioGRID",
                                'experiment': {
                                'link': None,
                                'display_name': "Positive Genetic",
                                'id': 49
                                },
                                'phenotype': None,
                                'id': 559335,
                                'annotation_type': "high-throughput"
                                }])
    
    def interaction_graph(self, identifier):
        return None
    
    def interaction_resources(self, identifier):
        return None
    
    #Literature
    def literature_overview(self, identifier):
        return json.dumps({'references':[], 'total_count': 5})
    
    def literature_details(self, identifier):
        return json.dumps({'additional':[], 'reviews':[], 'phenotype':[], 'go':[], 'interaction':[]})
    
    def literature_graph(self, identifier):
        return json.dumps([])
    
    #Phenotype
    def phenotype(self, identifier, callback=None):
        return None
    
    def phenotype_ontology_graph(self, identifier):
        return None
    
    def phenotype_overview(self, identifier):
        return None
    
    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None):
        return None
    
    def go_enrichment(self, bioent_ids, callback=None):
        return None
    
    #Protein
    def protein_domain_details(self, identifier):
        return None
    
    def regulation_overview(self, identifier):
        return None
    
    def regulation_details(self, identifier):
        return None
    
    def regulation_graph(self, identifier):
        return None
    
    def regulation_target_enrichment(self, identifier):
        return None
    
    #Binding
    def binding_site_details(self, identifier):
        return None

    #Misc
    def all_disambigs(self, min_id, max_id):
        return None
            