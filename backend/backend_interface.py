'''
Created on Oct 11, 2013

@author: kpaskov
'''
from abc import abstractmethod, ABCMeta

class BackendInterface:
    __metaclass__ = ABCMeta
    
    #Renderer
    @abstractmethod
    def get_renderer(self, method_name):
        return None
    
    #Response
    @abstractmethod
    def response_wrapper(self, method_name, request):
        return None
    
    #Disambigs
    @abstractmethod
    def all_disambigs(self, min_id, max_id):
        return None
    
    #Reference
    @abstractmethod
    def reference(self, identifier):
        return None
    
    @abstractmethod
    def all_references(self, min_id, max_id):
        return None
    
    @abstractmethod
    def all_bibentries(self, min_id, max_id):
        return None

    @abstractmethod
    def all_authors(self, min_id, max_id):
        return None
    
    @abstractmethod
    def reference_list(self, reference_ids):
        return None

    @abstractmethod
    def author(self, identifier):
        return None

    @abstractmethod
    def author_references(self, identifier):
        return None
    
    #Bioent
    @abstractmethod
    def all_bioentities(self, min_id, max_id):
        return None
    
    @abstractmethod
    def bioentity_list(self, bioent_ids):
        return None
    
    #Locus
    @abstractmethod
    def locus(self, identifier):
        return None
    
    @abstractmethod
    def locustabs(self, identifier):
        return None
    
    @abstractmethod
    def all_locustabs(self, min_id, max_id):
        return None
    
    #Biocon
    @abstractmethod
    def all_bioconcepts(self, min_id, max_id):
        return None

    #Chemical
    @abstractmethod
    def chemical(self, identifier):
        return None

    @abstractmethod
    def all_chemicals(self, min_id, max_id):
        return None
    
    #Go
    @abstractmethod
    def go(self, identifier):
        return None
    
    @abstractmethod
    def go_ontology_graph(self, identifier):
        return None
    
    @abstractmethod
    def go_overview(self, identifier):
        return None
    
    @abstractmethod
    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False):
        return None
    
    @abstractmethod
    def go_enrichment(self, identifier):
        return None

    @abstractmethod
    def go_graph(self, identifier):
        return None
    
    #Interaction
    @abstractmethod
    def interaction_overview(self, identifier):
        return None
    
    @abstractmethod
    def interaction_details(self, locus_identifier=None, reference_identifier=None):
        return None
    
    @abstractmethod
    def interaction_graph(self, identifier):
        return None
    
    @abstractmethod
    def interaction_resources(self, identifier):
        return None
    
    #Literature
    @abstractmethod
    def literature_overview(self, identifier):
        return None
    
    @abstractmethod
    def literature_details(self, locus_identifier=None, reference_identifier=None):
        return None
    
    @abstractmethod
    def literature_graph(self, identifier):
        return None
    
    #Phenotype
    @abstractmethod
    def phenotype(self, identifier):
        return None
    
    @abstractmethod
    def phenotype_ontology(self):
        return None
    
    @abstractmethod
    def phenotype_ontology_graph(self, identifier):
        return None
    
    @abstractmethod
    def phenotype_overview(self, identifier):
        return None
    
    @abstractmethod
    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False):
        return None

    @abstractmethod
    def phenotype_resources(self, identifier):
        return None

    @abstractmethod
    def phenotype_graph(self, identifier):
        return None
    
    #Protein
    @abstractmethod
    def protein_domain_details(self, locus_identifier=None, reference_identifier=None):
        return None
    
    #Regulation
    @abstractmethod
    def regulation_overview(self, identifier):
        return None
    
    @abstractmethod
    def regulation_details(self, locus_identifier=None, reference_identifier=None):
        return None
    
    @abstractmethod
    def regulation_graph(self, identifier):
        return None

    @abstractmethod
    def regulation_paragraph(self, identifier):
        return None
    
    @abstractmethod
    def regulation_target_enrichment(self, identifier):
        return None
    
    #Sequence
    @abstractmethod
    def binding_site_details(self, locus_identifier=None, reference_identifier=None):
        return None

