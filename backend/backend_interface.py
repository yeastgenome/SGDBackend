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
    
    #Reference
    @abstractmethod
    def reference(self, request):
        return None
    
    @abstractmethod
    def all_references(self, request):
        return None
    
    @abstractmethod
    def all_bibentries(self, request):
        return None
    
    @abstractmethod
    def reference_list(self, request):
        return None
    
    #Bioent
    @abstractmethod
    def all_bioentities(self, request):
        return None
    
    @abstractmethod
    def bioentity_list(self, request):
        return None
    
    #Locus
    @abstractmethod
    def locus(self, request):
        return None
    
    @abstractmethod
    def locustabs(self, request):
        return None
    
    #Biocon
    @abstractmethod
    def all_bioconcepts(self, request):
        return None
    
    @abstractmethod
    def bioconcept_list(self, request):
        return None
    
    #Go
    @abstractmethod
    def go(self, request):
        return None
    
    @abstractmethod
    def go_references(self, request):
        return None
    
    @abstractmethod
    def go_enrichment(self, request):
        return None
    
    #Interaction
    @abstractmethod
    def interaction_overview(self, request):
        return None
    
    @abstractmethod
    def interaction_details(self, request):
        return None
    
    @abstractmethod
    def interaction_graph(self, request):
        return None
    
    @abstractmethod
    def interaction_resources(self, request):
        return None
    
    @abstractmethod
    def interaction_references(self, request):
        return None
    
    #Literature
    @abstractmethod
    def literature_overview(self, request):
        return None
    
    @abstractmethod
    def literature_details(self, request):
        return None
    
    @abstractmethod
    def literature_graph(self, request):
        return None
    
    #Phenotype
    @abstractmethod
    def phenotype(self, request):
        return None
    
    @abstractmethod
    def phenotype_references(self, request):
        return None
    
    #Protein
    @abstractmethod
    def protein_domain_details(self, request):
        return None
    
    #Regulation
    @abstractmethod
    def regulation_overview(self, request):
        return None
    
    @abstractmethod
    def regulation_details(self, request):
        return None
    
    @abstractmethod
    def regulation_graph(self, request):
        return None
    
    @abstractmethod
    def regulation_references(self, request):
        return None
    
    #Sequence
    @abstractmethod
    def binding_site_details(self, request):
        return None
    
    #Misc
    @abstractmethod
    def all_disambigs(self, method_name):
        return None

    
    