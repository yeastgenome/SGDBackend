import sys

from src.sgd.convert import ConverterInterface
from src.sgd.convert.nex2perf import convert_core
from src.sgd.convert.nex2perf.convert_data import convert_data
from src.sgd.backend.perf import PerfBackend
from src.sgd.model import perf

__author__ = 'kpaskov'

class PerfPerfConverter(ConverterInterface):
    def __init__(self, perf1_dbtype, perf1_dbhost, perf1_dbname, perf1_schema, perf1_dbuser, perf1_dbpass,
                 perf2_dbtype, perf2_dbhost, perf2_dbname, perf2_schema, perf2_dbuser, perf2_dbpass):
        self.session_maker = prepare_schema_connection(perf, perf2_dbtype, perf2_dbhost, perf2_dbname, perf2_schema, perf2_dbuser, perf2_dbpass)
        check_session_maker(self.session_maker, perf2_dbhost, perf2_schema)
        
        self.backend = PerfBackend(perf1_dbtype, perf1_dbhost, perf1_dbname, perf1_schema, perf1_dbuser, perf1_dbpass, None)

        self.log = set_up_logging('perf_perf_converter')
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

    def convert_basic(self):
        self.core_wrapper(convert_core.convert_bioentity, 1000)
        #1.24.14 First Load (sgd-dev): :13
        self.core_wrapper(convert_core.convert_bioconcept, 10000)
        #1.24.14 First Load (sgd-dev): :12
        self.core_wrapper(convert_core.convert_chemical, 1000)
        #1.24.14 First Load (sgd-dev): :20
        self.core_wrapper(convert_core.convert_author, None)
        #1.24.14 First Load (sgd-dev): 3:05
        self.core_wrapper(convert_core.convert_disambig, 10000)
        self.core_wrapper(convert_core.convert_ontology, None)

    def convert_basic_continued(self):
        from src.sgd.model.perf.author_data import AuthorDetails
        from src.sgd.model.perf.core import Author

        author_ids = [x.id for x in self.session_maker().query(Author.id).all()]

        self.data_wrapper(AuthorDetails, "REFERENCE", 'author_id', lambda x: self.backend.author_references(x, are_ids=True), 'author_details', author_ids, 1000)

    def convert_reference(self):
        #1.24.14 First Load (sgd-dev): 17:12
        self.core_wrapper(convert_core.convert_reference, 100)

    def convert_interaction(self):
        from src.sgd.model.perf.bioentity_data import BioentityOverview, BioentityGraph, BioentityResources, BioentityDetails
        from src.sgd.model.perf.reference_data import ReferenceDetails
        from src.sgd.model.perf.core import Bioentity, Reference

        locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]

        #1.24.14 First Load (sgd-dev): 8:09
        self.data_wrapper(BioentityOverview, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_overview(x, are_ids=True), 'interaction_overview', locus_ids, 1000)

        #1.24.14 First Load (sgd-dev): 13:35
        self.data_wrapper(BioentityGraph, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_graph(x, are_ids=True), 'interaction_graph', locus_ids, 1000)

        #1.24.14 First Load (sgd-dev): 6:52
        self.data_wrapper(BioentityResources, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_resources(x, are_ids=True), 'interaction_resources', locus_ids, 1000)

        #1.25.14 First Load (sgd-dev): 53:59
        self.data_wrapper(BioentityDetails, "INTERACTION", 'bioentity_id', lambda x: self.backend.interaction_details(locus_identifier=x, are_ids=True), 'interaction_details', locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "INTERACTION", 'reference_id', lambda x: self.backend.interaction_details(reference_identifier=x, are_ids=True), 'interaction_details', reference_ids, 1000)

    def convert_literature(self):
        from src.sgd.model.perf.bioentity_data import BioentityOverview, BioentityGraph, BioentityDetails
        from src.sgd.model.perf.reference_data import ReferenceDetails
        from src.sgd.model.perf.core import Bioentity, Reference

        locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]

        #1.24.14 First Load (sgd-dev): 11:38
        self.data_wrapper(BioentityOverview, "LITERATURE", 'bioentity_id', lambda x: self.backend.literature_overview(x, are_ids=True), 'literature_overview', locus_ids, 1000)

        #1.24.14 First Load (sgd-dev): 14:07
        self.data_wrapper(BioentityGraph, "LITERATURE", 'bioentity_id', lambda x: self.backend.literature_graph(x, are_ids=True), 'literature_graph', locus_ids, 1000)

        self.data_wrapper(BioentityDetails, "LITERATURE", 'bioentity_id', lambda x: self.backend.literature_details(locus_identifier=x), 'literature_details', locus_ids, 100)
        self.data_wrapper(ReferenceDetails, "LITERATURE", 'reference_id', lambda x: self.backend.literature_details(reference_identifier=x, are_ids=True), 'literature_details', reference_ids, 1000)

    def convert_regulation(self):
        from src.sgd.model.perf.bioentity_data import BioentityOverview, BioentityGraph, BioentityEnrichment, BioentityParagraph, BioentityDetails
        from src.sgd.model.perf.reference_data import ReferenceDetails
        from src.sgd.model.perf.core import Bioentity, Reference

        locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]

        self.data_wrapper(BioentityOverview, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_overview(x, are_ids=True), 'regulation_overview', locus_ids, 1000)

        #1.24.14 First Load (sgd-dev): 31:31
        self.data_wrapper(BioentityGraph, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_graph(x, are_ids=True), 'regulation_graph', locus_ids, 1000)

        self.data_wrapper(BioentityEnrichment, "REGULATION_TARGET", 'bioentity_id', lambda x: self.backend.regulation_target_enrichment(x, are_ids=True), 'regulation_target_enrichment', locus_ids, 100)

        #1.24.14 First Load (sgd-dev): 7:22
        self.data_wrapper(BioentityParagraph, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_paragraph(x, are_ids=True), 'regulation_paragraph', locus_ids, 1000)

        #1.25.14 First Load (sgd-dev): 1:59:29
        self.data_wrapper(BioentityDetails, "REGULATION", 'bioentity_id', lambda x: self.backend.regulation_details(locus_identifier=x, are_ids=True), 'regulation_details', locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "REGULATION", 'reference_id', lambda x: self.backend.regulation_details(reference_identifier=x, are_ids=True), 'regulation_details', reference_ids, 1000)

    def convert_go(self):
        from src.sgd.model.perf.bioentity_data import BioentityOverview, BioentityGraph, BioentityDetails
        from src.sgd.model.perf.bioconcept_data import BioconceptGraph, BioconceptDetails
        from src.sgd.model.perf.reference_data import ReferenceDetails
        from src.sgd.model.perf.core import Bioentity, Reference, Bioconcept

        locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]
        go_ids = [x.id for x in self.session_maker().query(Bioconcept.id).all()]

        #1.24.14 First Load (sgd-dev): 9:26
        self.data_wrapper(BioentityOverview, "GO", 'bioentity_id', lambda x: self.backend.go_overview(x, are_ids=True), 'go_overview', locus_ids, 1000)

        self.data_wrapper(BioentityGraph, "GO", 'bioentity_id', lambda x: self.backend.go_graph(x, are_ids=True), 'go_graph', locus_ids, 1000)

        #1.24.14 First Load (sgd-dev): 1:01:33
        self.data_wrapper(BioconceptGraph, "ONTOLOGY", 'bioconcept_id', lambda x: self.backend.go_ontology_graph(x, are_ids=True), 'go_ontology_graph', go_ids, 1000)

        #1.25.14 First Load (sgd-dev): 17:20
        self.data_wrapper(BioentityDetails, "GO", 'bioentity_id', lambda x: self.backend.go_details(locus_identifier=x, are_ids=True), 'go_details', locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "GO", 'reference_id', lambda x: self.backend.go_details(reference_identifier=x, are_ids=True), 'go_details', reference_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS", 'bioconcept_id', lambda x: self.backend.go_details(go_identifier=x, are_ids=True), 'locus_details', go_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS_ALL_CHILDREN", 'bioconcept_id', lambda x: self.backend.go_details(go_identifier=x, with_children=True, are_ids=True), 'locus_details', go_ids, 1000)

    def convert_phenotype(self):
        from src.sgd.model.perf.bioentity_data import BioentityOverview, BioentityGraph, BioentityResources, BioentityDetails
        from src.sgd.model.perf.bioconcept_data import BioconceptOverview, BioconceptGraph, BioconceptDetails
        from src.sgd.model.perf.reference_data import ReferenceDetails
        from src.sgd.model.perf.chemical_data import ChemicalDetails
        from src.sgd.model.perf.core import Bioentity, Reference, Bioconcept, Chemical

        locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]
        reference_ids = [x.id for x in self.session_maker().query(Reference.id).all()]
        phenotype_ids = [x.id for x in self.session_maker().query(Bioconcept.id).all()]
        chemical_ids = [x.id for x in self.session_maker().query(Chemical.id).all()]

        #1.24.14 First Load (sgd-dev): 10:17
        self.data_wrapper(BioentityOverview, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_overview(locus_identifier=x, are_ids=True), 'phenotype_overview', locus_ids, 1000)
        self.data_wrapper(BioconceptOverview, "PHENOTYPE", 'bioconcept_id', lambda x: self.backend.phenotype_overview(phenotype_identifier=x, are_ids=True), 'phenotype_overview', phenotype_ids, 1000)

        #1.26.14 First Load (sgd-dev): 3:54:09
        self.data_wrapper(BioentityGraph, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_graph(x, are_ids=True), 'phenotype_graph', locus_ids, 100)

        #1.24.14 First Load (sgd-dev): 7:22
        self.data_wrapper(BioentityResources, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_resources(x, are_ids=True), 'phenotype_resources', locus_ids, 1000)

        #1.25.14 First Load (sgd-dev): 3:46
        self.data_wrapper(BioconceptGraph, "ONTOLOGY", 'bioconcept_id', lambda x: self.backend.phenotype_ontology_graph(x, are_ids=True), 'phenotype_ontology_graph', phenotype_ids, 1000)

        #1.25.14 First Load (sgd-dev): 19:18
        self.data_wrapper(BioentityDetails, "PHENOTYPE", 'bioentity_id', lambda x: self.backend.phenotype_details(locus_identifier=x, are_ids=True), 'phenotype_details', locus_ids, 1000)
        self.data_wrapper(ReferenceDetails, "PHENOTYPE", 'reference_id', lambda x: self.backend.phenotype_details(reference_identifier=x, are_ids=True), 'phenotype_details', reference_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS", 'bioconcept_id', lambda x: self.backend.phenotype_details(phenotype_identifier=x, are_ids=True), 'locus_details', phenotype_ids, 1000)
        self.data_wrapper(BioconceptDetails, "LOCUS_ALL_CHILDREN", 'bioconcept_id', lambda x: self.backend.phenotype_details(phenotype_identifier=x, with_children=True, are_ids=True), 'locus_details', phenotype_ids, 1000)
        self.data_wrapper(ChemicalDetails, "PHENOTYPE", 'chemical_id', lambda x: self.backend.phenotype_details(chemical_identifier=x, are_ids=True), 'phenotype_details', chemical_ids, 1000)

    def convert_protein(self):
        from src.sgd.model.perf.bioentity_data import BioentityDetails
        from src.sgd.model.perf.core import Bioentity

        locus_ids = [x.id for x in self.session_maker().query(Bioentity.id).all()]

        self.data_wrapper(BioentityDetails, "DOMAIN", 'bioentity_id', lambda x: self.backend.protein_domain_details(locus_identifier=x, are_ids=True), 'protein_domain_details', locus_ids, 1000)
        self.data_wrapper(BioentityDetails, "BINDING", 'bioentity_id', lambda x: self.backend.binding_site_details(locus_identifier=x, are_ids=True), 'binding_site_details', locus_ids, 1000)

if __name__ == "__main__":
    from src.sgd.convert import config, check_session_maker, prepare_schema_connection, set_up_logging

    if len(sys.argv) == 4:
        nex_dbhost = sys.argv[1]
        perf_dbhost = sys.argv[2]
        method = sys.argv[3]
        converter = PerfPerfConverter(config.NEX_DBTYPE, nex_dbhost, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS,
                                     config.PERF_DBTYPE, perf_dbhost, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
        getattr(converter, method)()
    else:
        print 'Please enter nex_dbhost, perf_dbhost, and method.'
