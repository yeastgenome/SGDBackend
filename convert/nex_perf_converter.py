'''
Created on Oct 11, 2013

@author: kpaskov
'''
import json
from convert.converter_interface import ConverterInterface
from convert_perf import convert_core
from convert_perf.convert_data import convert_data
from convert_utils import prepare_schema_connection, check_session_maker, \
    set_up_logging
from sgdbackend import SGDBackend
import model_perf_schema
import sys

class NexPerfConverter(ConverterInterface):    
    def __init__(self, nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass,
                 perf_dbtype, perf_dbhost, perf_dbname, perf_schema, perf_dbuser, perf_dbpass):
        self.session_maker = prepare_schema_connection(model_perf_schema, perf_dbtype, perf_dbhost, perf_dbname, perf_schema, perf_dbuser, perf_dbpass)
        check_session_maker(self.session_maker, perf_dbhost, perf_schema)
        
        self.backend = SGDBackend(nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass, None)

        self.log = set_up_logging('nex_perf_converter')
        print 'Ready'

    def core_wrapper(self, f, chunk_size):
        try:
            f(self.session_maker, self.backend, self.log, chunk_size)
        except Exception:
            self.log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
            
    def data_wrapper(self, cls, class_type, obj_type, new_obj_f, label, obj_ids, chunk_size):
        try:
            self.log.info(label)
            convert_data(self.session_maker, cls, class_type, obj_type, new_obj_f, self.log, obj_ids, chunk_size)
        except Exception:
            self.log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )

    def load_ids(self):
        from model_perf_schema.core import Bioentity, Bioconcept, Reference, Chemical, Author
        self.locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        bioconcepts = self.session_maker().query(Bioconcept.id).all()
        self.phenotype_ids = [x.id for x in bioconcepts]
        self.go_ids = [x.id for x in bioconcepts]
        self.reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]
        self.chemical_ids = [x.id for x in self.session_maker().query(Chemical.id).all()]
        self.author_ids = [x.id for x in self.session_maker().query(Author.id).all()]
    
    def convert_all(self):
        #Core
        self.convert_bioentity()
        self.convert_bioconcept()
        self.convert_reference()
        self.convert_chemical()
        self.convert_author()
        self.convert_disambig()
        self.convert_ontology()

        self.load_ids()
        
        #Data

        self.convert_author_details()

        self.convert_interaction_overview()
        self.convert_interaction_details()
        self.convert_interaction_graph()
        self.convert_interaction_resources()
        
        self.convert_literature_overview()
        self.convert_literature_details()
        self.convert_literature_graph()
        
        self.convert_protein_domain_details()
        
        self.convert_binding_site_details()
        
        self.convert_regulation_overview()
        self.convert_regulation_paragraph()
        self.convert_regulation_details()
        self.convert_regulation_graph()
        self.convert_regulation_target_enrich()

        self.convert_phenotype_details()
        self.convert_phenotype_overview()
        self.convert_phenotype_graph()
        self.convert_phenotype_resources()
        self.convert_phenotype_ontology_graph()

        self.convert_go_details()
        self.convert_go_overview()
        self.convert_go_graph()
        self.convert_go_ontology_graph()
        
    def convert_daily(self):
        #Core
        self.convert_bioentity()
        self.convert_bioconcept()
        self.convert_reference()
        self.convert_chemical()
        self.convert_author()
        self.convert_disambig()
        self.convert_ontology()

        self.load_ids()
        
        #Data
        self.convert_author_details()

        self.convert_literature_overview()
        self.convert_literature_details()
        self.convert_literature_graph()

        self.convert_phenotype_details()
        self.convert_phenotype_overview()
        self.convert_phenotype_graph()
        self.convert_phenotype_resources()
        self.convert_phenotype_ontology_graph()

        self.convert_go_details()
        self.convert_go_overview()
        self.convert_go_graph()
        self.convert_go_ontology_graph()
        
    def convert_monthly(self):

        from model_perf_schema.core import Bioentity, Bioconcept, Reference, Chemical, Author
        self.locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        self.reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]

        #Data
        self.convert_interaction_overview()
        self.convert_interaction_details()
        self.convert_interaction_graph()
        self.convert_interaction_resources()
        
    def convert_updated_flatfiles(self):

        from model_perf_schema.core import Bioentity, Bioconcept, Reference, Chemical, Author
        self.locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        self.reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]

        #Data
        self.convert_protein_domain_details()
        
        self.convert_binding_site_details()
        
        self.convert_regulation_overview()
        self.convert_regulation_details()
        self.convert_regulation_graph()
        self.convert_regulation_target_enrich()
        
    def convert_bioentity(self):
        self.core_wrapper(convert_core.convert_bioentity, 1000)
    def convert_bioconcept(self):
        #1.24.14 First Load (sgd-dev): :13
        self.core_wrapper(convert_core.convert_bioconcept, 10000)
    def convert_reference(self):
        #1.24.14 First Load (sgd-dev): 17:12
        self.core_wrapper(convert_core.convert_reference, 100)
    def convert_chemical(self):
        #1.24.14 First Load (sgd-dev): :12
        self.core_wrapper(convert_core.convert_chemical, 1000)
    def convert_author(self):
        #1.24.14 First Load (sgd-dev): :20
        self.core_wrapper(convert_core.convert_author, None)
    def convert_disambig(self):
        #1.24.14 First Load (sgd-dev): 3:05
        self.core_wrapper(convert_core.convert_disambig, 10000)

    def convert_ontology(self):
        self.core_wrapper(convert_core.convert_ontology, None)

    def convert_interaction_overview(self):
        #1.24.14 First Load (sgd-dev): 8:09
        from model_perf_schema.bioentity_data import BioentityOverview
        self.data_wrapper(BioentityOverview, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_overview(x, are_ids=True), 'interaction_overview', self.locus_ids, 1000)
    def convert_interaction_graph(self):
        #1.24.14 First Load (sgd-dev): 13:35
        from model_perf_schema.bioentity_data import BioentityGraph
        self.data_wrapper(BioentityGraph, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_graph(x, are_ids=True), 'interaction_graph', self.locus_ids, 1000)
    def convert_interaction_resources(self):
        #1.24.14 First Load (sgd-dev): 6:52
        from model_perf_schema.bioentity_data import BioentityResources
        self.data_wrapper(BioentityResources, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_resources(x, are_ids=True), 'interaction_resources', self.locus_ids, 1000)

    def convert_literature_overview(self):
        #1.24.14 First Load (sgd-dev): 11:38
        from model_perf_schema.bioentity_data import BioentityOverview
        self.data_wrapper(BioentityOverview, "LITERATURE", 'bioentity_id', lambda x: self.backend.literature_overview(x, are_ids=True), 'literature_overview', self.locus_ids, 1000)
    def convert_literature_graph(self):
        #1.24.14 First Load (sgd-dev): 14:07
        from model_perf_schema.bioentity_data import BioentityGraph
        self.data_wrapper(BioentityGraph, "LITERATURE", 'bioentity_id', lambda x: self.backend.literature_graph(x, are_ids=True), 'literature_graph', self.locus_ids, 1000)

    def convert_regulation_overview(self):
        from model_perf_schema.bioentity_data import BioentityOverview
        self.data_wrapper(BioentityOverview, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_overview(x, are_ids=True), 'regulation_overview', self.locus_ids, 1000)
    def convert_regulation_graph(self):
        #1.24.14 First Load (sgd-dev): 31:31
        from model_perf_schema.bioentity_data import BioentityGraph
        self.data_wrapper(BioentityGraph, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_graph(x, are_ids=True), 'regulation_graph', self.locus_ids, 1000)
    def convert_regulation_target_enrich(self):
        from model_perf_schema.bioentity_data import BioentityEnrichment
        self.data_wrapper(BioentityEnrichment, "REGULATION_TARGET", 'bioentity_id', lambda x: self.backend.regulation_target_enrichment(x, are_ids=True), 'regulation_target_enrichment', self.locus_ids, 100)
    def convert_regulation_paragraph(self):
        #1.24.14 First Load (sgd-dev): 7:22
        from model_perf_schema.bioentity_data import BioentityParagraph
        self.data_wrapper(BioentityParagraph, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_paragraph(x, are_ids=True), 'regulation_paragraph', self.locus_ids, 1000)

    def convert_go_overview(self):
        #1.24.14 First Load (sgd-dev): 9:26
        from model_perf_schema.bioentity_data import BioentityOverview
        self.data_wrapper(BioentityOverview, "GO", 'bioentity_id', lambda x: self.backend.go_overview(x, are_ids=True), 'go_overview', self.locus_ids, 1000)
    def convert_go_graph(self):
        from model_perf_schema.bioentity_data import BioentityGraph
        self.data_wrapper(BioentityGraph, "GO", 'bioentity_id', lambda x: self.backend.go_graph(x, are_ids=True), 'go_graph', self.locus_ids, 1000)
    def convert_go_ontology_graph(self):
        #1.24.14 First Load (sgd-dev): 1:01:33
        from model_perf_schema.bioconcept_data import BioconceptGraph
        self.data_wrapper(BioconceptGraph, "ONTOLOGY", 'bioconcept_id', lambda x: self.backend.go_ontology_graph(x, are_ids=True), 'go_ontology_graph', self.go_ids, 1000)

    def convert_phenotype_overview(self):
        #1.24.14 First Load (sgd-dev): 10:17
        from model_perf_schema.bioconcept_data import BioconceptOverview
        from model_perf_schema.bioentity_data import BioentityOverview
        self.data_wrapper(BioentityOverview, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_overview(locus_identifier=x, are_ids=True), 'phenotype_overview', self.locus_ids, 1000)
        self.data_wrapper(BioconceptOverview, "PHENOTYPE", 'bioconcept_id', lambda x: self.backend.phenotype_overview(phenotype_identifier=x, are_ids=True), 'phenotype_overview', self.phenotype_ids, 1000)
    def convert_phenotype_graph(self):
        #1.26.14 First Load (sgd-dev): 3:54:09
        from model_perf_schema.bioentity_data import BioentityGraph
        self.data_wrapper(BioentityGraph, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_graph(x, are_ids=True), 'phenotype_graph', self.locus_ids, 100)
    def convert_phenotype_resources(self):
        #1.24.14 First Load (sgd-dev): 7:22
        from model_perf_schema.bioentity_data import BioentityResources
        self.data_wrapper(BioentityResources, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_resources(x, are_ids=True), 'phenotype_resources', self.locus_ids, 1000)
    def convert_phenotype_ontology_graph(self):
        #1.25.14 First Load (sgd-dev): 3:46
        from model_perf_schema.bioconcept_data import BioconceptGraph
        self.data_wrapper(BioconceptGraph, "ONTOLOGY", 'bioconcept_id', lambda x: self.backend.phenotype_ontology_graph(x, are_ids=True), 'phenotype_ontology_graph', self.phenotype_ids, 1000)


    def convert_interaction_details(self):
        #1.25.14 First Load (sgd-dev): 53:59
        from model_perf_schema.bioentity_data import BioentityDetails
        from model_perf_schema.reference_data import ReferenceDetails
        self.data_wrapper(BioentityDetails, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_details(locus_identifier=x, are_ids=True), 'interaction_details', self.locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "INTERACTION", 'reference_id', lambda x: self.backend.interaction_details(reference_identifier=x, are_ids=True), 'interaction_details', self.reference_ids, 1000)
    def convert_literature_details(self):
        from model_perf_schema.bioentity_data import BioentityDetails
        from model_perf_schema.reference_data import ReferenceDetails
        #self.data_wrapper(BioentityDetails, "LITERATURE", 'bioentity_id', lambda x: self.backend.literature_details(locus_identifier=x), 'literature_details', self.locus_ids, 100)
        self.data_wrapper(ReferenceDetails, "LITERATURE", 'reference_id', lambda x: self.backend.literature_details(reference_identifier=x, are_ids=True), 'literature_details', self.reference_ids, 1000)
    def convert_protein_domain_details(self):
        from model_perf_schema.bioentity_data import BioentityDetails
        self.data_wrapper(BioentityDetails, "DOMAIN", 'bioentity_id', lambda x: self.backend.protein_domain_details(locus_identifier=x, are_ids=True), 'protein_domain_details', self.locus_ids, 1000)
    def convert_binding_site_details(self):
        from model_perf_schema.bioentity_data import BioentityDetails
        self.data_wrapper(BioentityDetails, "BINDING", 'bioentity_id', lambda x: self.backend.binding_site_details(locus_identifier=x, are_ids=True), 'binding_site_details', self.locus_ids, 1000)
    def convert_regulation_details(self):
        #1.25.14 First Load (sgd-dev): 1:59:29
        from model_perf_schema.bioentity_data import BioentityDetails
        from model_perf_schema.reference_data import ReferenceDetails
        self.data_wrapper(BioentityDetails, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_details(locus_identifier=x, are_ids=True), 'regulation_details', self.locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "REGULATION", 'reference_id', lambda x: self.backend.regulation_details(reference_identifier=x, are_ids=True), 'regulation_details', self.reference_ids, 1000)
    def convert_go_details(self):
        #1.25.14 First Load (sgd-dev): 17:20
        from model_perf_schema.bioentity_data import BioentityDetails
        from model_perf_schema.reference_data import ReferenceDetails
        from model_perf_schema.bioconcept_data import BioconceptDetails
        self.data_wrapper(BioentityDetails, "GO", 'bioentity_id', lambda x: self.backend.go_details(locus_identifier=x, are_ids=True), 'go_details', self.locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "GO", 'reference_id', lambda x: self.backend.go_details(reference_identifier=x, are_ids=True), 'go_details', self.reference_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS", 'bioconcept_id', lambda x: self.backend.go_details(go_identifier=x, are_ids=True), 'locus_details', self.go_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS_ALL_CHILDREN", 'bioconcept_id', lambda x: self.backend.go_details(go_identifier=x, with_children=True, are_ids=True), 'locus_details', self.go_ids, 1000)
    def convert_phenotype_details(self):
        #1.25.14 First Load (sgd-dev): 19:18
        from model_perf_schema.bioentity_data import BioentityDetails
        from model_perf_schema.reference_data import ReferenceDetails
        from model_perf_schema.bioconcept_data import BioconceptDetails
        from model_perf_schema.chemical_data import ChemicalDetails
        self.data_wrapper(BioentityDetails, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_details(locus_identifier=x, are_ids=True), 'phenotype_details', self.locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "PHENOTYPE", 'reference_id', lambda x: self.backend.phenotype_details(reference_identifier=x, are_ids=True), 'phenotype_details', self.reference_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS", 'bioconcept_id', lambda x: self.backend.phenotype_details(phenotype_identifier=x, are_ids=True), 'locus_details', self.phenotype_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS_ALL_CHILDREN", 'bioconcept_id', lambda x: self.backend.phenotype_details(phenotype_identifier=x, with_children=True, are_ids=True), 'locus_details', self.phenotype_ids, 1000)
        self.data_wrapper(ChemicalDetails, "PHENOTYPE", 'chemical_id', lambda x: self.backend.phenotype_details(chemical_identifier=x, are_ids=True), 'phenotype_details', self.chemical_ids, 1000)
    def convert_author_details(self):
        from model_perf_schema.author_data import AuthorDetails
        self.data_wrapper(AuthorDetails, "REFERENCE", 'author_id', lambda x: self.backend.author_references(x, are_ids=True), 'author_details', self.author_ids, 1000)

if __name__ == "__main__":
    from convert import config

    if len(sys.argv) == 4:
        nex_dbhost = sys.argv[1]
        perf_dbhost = sys.argv[2]
        method = sys.argv[3]
        converter = NexPerfConverter(config.NEX_DBTYPE, nex_dbhost, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, 
                                     config.PERF_DBTYPE, perf_dbhost, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
        getattr(converter, method)()
    else:
        print 'Please enter nex_dbhost, perf_dbhost, and method.'
