from abc import abstractmethod, ABCMeta

__author__ = 'kpaskov'

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
    def reference(self, reference_identifier):
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
    def author(self, author_identifier):
        return None

    @abstractmethod
    def author_references(self, author_identifier):
        return None

    @abstractmethod
    def references_this_week(self):
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
    def locus(self, locus_identifier):
        return None

    @abstractmethod
    def locus_alias(self, locus_identifier):
        return None
    
    @abstractmethod
    def locustabs(self, locus_identifier):
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
    def chemical(self, chemical_identifier):
        return None

    @abstractmethod
    def all_chemicals(self, min_id, max_id):
        return None

    #Domain
    @abstractmethod
    def domain(self, domain_identifier):
        return None

    #Contig
    @abstractmethod
    def contig(self, contig_identifier):
        return None

    #ECNumber
    @abstractmethod
    def ec_number(self, ec_number_identifier):
        return None

    @abstractmethod
    def ec_number_ontology_graph(self, ec_number_identifier):
        return None

    @abstractmethod
    def ec_number_details(self, locus_identifier=None, ec_number_identifier=None, with_children=False):
        return None

    #Go
    @abstractmethod
    def go(self, go_identifier):
        return None
    
    @abstractmethod
    def go_ontology_graph(self, go_identifier):
        return None
    
    @abstractmethod
    def go_overview(self, locus_identifier):
        return None
    
    @abstractmethod
    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False):
        return None
    
    @abstractmethod
    def go_enrichment(self, locus_identifier):
        return None

    @abstractmethod
    def go_graph(self, locus_identifier):
        return None
    
    #Interaction
    @abstractmethod
    def interaction_overview(self, locus_identifier):
        return None
    
    @abstractmethod
    def interaction_details(self, locus_identifier=None, reference_identifier=None, ids_only=False):
        return None
    
    @abstractmethod
    def interaction_graph(self, locus_identifier):
        return None
    
    @abstractmethod
    def interaction_resources(self, locus_identifier):
        return None
    
    #Literature
    @abstractmethod
    def literature_overview(self, locus_identifier):
        return None
    
    @abstractmethod
    def literature_details(self, locus_identifier=None, reference_identifier=None):
        return None
    
    @abstractmethod
    def literature_graph(self, locus_identifier):
        return None
    
    #Phenotype
    @abstractmethod
    def phenotype(self, phenotype_identifier):
        return None

    @abstractmethod
    def phenotype_ontology(self):
        return None
    
    @abstractmethod
    def phenotype_ontology_graph(self, phenotype_identifier):
        return None
    
    @abstractmethod
    def phenotype_overview(self, locus_identifier):
        return None
    
    @abstractmethod
    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False):
        return None

    @abstractmethod
    def phenotype_resources(self, locus_identifier):
        return None

    @abstractmethod
    def phenotype_graph(self, locus_identifier):
        return None

    #Protein
    @abstractmethod
    def protein_overview(self, locus_identifier):
        return None

    @abstractmethod
    def sequence_overview(self, locus_identifier):
        return None

    @abstractmethod
    def protein_domain_details(self, locus_identifier=None, domain_identifier=None):
        return None

    @abstractmethod
    def ec_number_details(self, locus_identifier=None, ec_number_identifier=None):
        return None

    @abstractmethod
    def protein_domain_graph(self, locus_identifier):
        return None

    @abstractmethod
    def protein_resources(self, locus_identifier):
        return None
    
    #Regulation
    @abstractmethod
    def regulation_overview(self, locus_identifier):
        return None
    
    @abstractmethod
    def regulation_details(self, locus_identifier=None, reference_identifier=None):
        return None
    
    @abstractmethod
    def regulation_graph(self, locus_identifier):
        return None

    @abstractmethod
    def regulation_paragraph(self, locus_identifier):
        return None
    
    @abstractmethod
    def regulation_target_enrichment(self, locus_identifier):
        return None
    
    #Sequence
    @abstractmethod
    def binding_site_details(self, locus_identifier=None, reference_identifier=None):
        return None

    @abstractmethod
    def sequence_details(self, locus_identifier):
        return None

    @abstractmethod
    def protein_phosphorylation_details(self, locus_identifier):
        return None

    @abstractmethod
    def protein_experiment_details(self, locus_identifier):
        return None

