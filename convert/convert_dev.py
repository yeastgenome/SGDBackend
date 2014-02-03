'''
Created on Oct 24, 2013

@author: kpaskov
'''

from convert import config
from convert.bud_nex_converter import BudNexConverter
from convert.nex_perf_converter import NexPerfConverter

if __name__ == "__main__":   
    #Pastry -> Dev_nex
    #pastry_dev_converter = BudNexConverter(config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS,
    #                                config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    #pastry_dev_converter.convert_protein_domain()
    #pastry_dev_converter.convert_daily()
    #pastry_dev_converter.convert_bioitem()

    #pastry_dev_converter.convert_evelements()
    #pastry_dev_converter.convert_reference()
    #pastry_dev_converter.convert_bioentity()
    #pastry_dev_converter.convert_bioconcept()
    #pastry_dev_converter.convert_bioitem()
    #pastry_dev_converter.convert_chemical()

    #pastry_dev_converter.convert_interaction()
    #pastry_dev_converter.convert_literature()

    #pastry_dev_converter.convert_phenotype()
    #pastry_dev_converter.convert_go()

    #pastry_dev_converter.convert_bioentity_in_depth()
    #pastry_dev_converter.convert_bioconcept_in_depth()
    #pastry_dev_converter.convert_chemical_in_depth()
    #pastry_dev_converter.convert_reference_in_depth()


    #Dev_nex -> Dev_perf
    dev_perf_converter = NexPerfConverter(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS,
                                     config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    #dev_perf_converter.convert_daily()
    #dev_perf_converter.convert_bioentity()
    #dev_perf_converter.convert_bioconcept()
    #dev_perf_converter.convert_author()
    #dev_perf_converter.convert_reference()
    #dev_perf_converter.convert_chemical()
    #dev_perf_converter.convert_disambig()

    #dev_perf_converter.convert_interaction_details()
    #dev_perf_converter.convert_interaction_overview()
    #dev_perf_converter.convert_interaction_graph()
    #dev_perf_converter.convert_interaction_resources()

    #dev_perf_converter.convert_literature_details()
    #dev_perf_converter.convert_literature_overview()
    #dev_perf_converter.convert_literature_graph()

    #dev_perf_converter.convert_go_details()
    #dev_perf_converter.convert_go_overview()
    #dev_perf_converter.convert_go_graph()
    #dev_perf_converter.convert_go_ontology_graph()

    #dev_perf_converter.convert_regulation_details()
    #dev_perf_converter.convert_protein_domain_details()
    #dev_perf_converter.convert_binding_site_details()
    #dev_perf_converter.convert_regulation_overview()
    #dev_perf_converter.convert_regulation_graph()
    #dev_perf_converter.convert_regulation_paragraph()
    #dev_perf_converter.convert_regulation_target_enrich()

    dev_perf_converter.convert_phenotype_details()
    #dev_perf_converter.convert_phenotype_overview()
    #dev_perf_converter.convert_phenotype_graph()
    #dev_perf_converter.convert_phenotype_resources()
    #dev_perf_converter.convert_phenotype_ontology_graph()

    #dev_perf_converter.convert_ontology()
    #dev_perf_converter.convert_author_details()


