'''
Created on Oct 24, 2013

@author: kpaskov
'''
import threading

from convert import config
from convert.bud_nex_converter import BudNexConverter
from convert.nex_perf_converter import NexPerfConverter
from convert.perf_perf_converter import PerfPerfConverter

if __name__ == "__main__":   
    #Pastry -> Master
    pastry_master_converter = BudNexConverter(config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS,
                                    config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    pastry_master_converter.convert_core()
    pastry_master_converter.convert_qualifier()

    #Master -> DB1
    master_db1_converter = NexPerfConverter(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS,
                                     config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    master_db1_converter.convert_bioentity()
    master_db1_converter.convert_bioconcept()
    master_db1_converter.convert_chemical()
    master_db1_converter.convert_author()
    master_db1_converter.convert_disambig()
    master_db1_converter.convert_ontology()
    master_db1_converter.load_ids()

    #DB1 -> DB2
    db1_db2_converter = PerfPerfConverter(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS,
                                     config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    db1_db2_converter.convert_bioentity()
    db1_db2_converter.convert_bioconcept()
    db1_db2_converter.convert_chemical()
    db1_db2_converter.convert_author()
    db1_db2_converter.convert_disambig()
    db1_db2_converter.convert_ontology()
    db1_db2_converter.load_ids()

    class ReferenceThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = 'Reference'
        def run(self):
            pastry_master_converter.convert_reference_in_depth()

            master_db1_converter.convert_reference()

            db1_db2_converter.convert_reference()
    ReferenceThread().start()

    class PhenotypeGraphsThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = 'Phenotype Graphs'
        def run(self):
            master_db1_converter.convert_phenotype_graph()
            master_db1_converter.convert_phenotype_ontology_graph()

            db1_db2_converter.convert_phenotype_graph()
            db1_db2_converter.convert_phenotype_ontology_graph()

    class PhenotypeThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = 'Phenotype'
        def run(self):
            pastry_master_converter.convert_phenotype()

            PhenotypeGraphsThread().start()

            master_db1_converter.convert_phenotype_details()
            master_db1_converter.convert_phenotype_overview()
            master_db1_converter.convert_phenotype_resources()

            db1_db2_converter.convert_phenotype_details()
            db1_db2_converter.convert_phenotype_overview()
            db1_db2_converter.convert_phenotype_resources()
    PhenotypeThread().start()

    class LiteratureThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = 'Literature'
        def run(self):
            pastry_master_converter.convert_literature()

            master_db1_converter.convert_literature_overview()
            master_db1_converter.convert_literature_details()
            master_db1_converter.convert_literature_graph()

            db1_db2_converter.convert_literature_overview()
            db1_db2_converter.convert_literature_details()
            db1_db2_converter.convert_literature_graph()
    LiteratureThread().start()

    class GoGraphThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = 'Go'
        def run(self):
            master_db1_converter.convert_go_graph()
            master_db1_converter.convert_go_ontology_graph()

            db1_db2_converter.convert_go_graph()
            db1_db2_converter.convert_go_ontology_graph()

    class GoThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = 'Go'
        def run(self):
            pastry_master_converter.convert_go()

            GoGraphThread().start()

            master_db1_converter.convert_go_details()
            master_db1_converter.convert_go_overview()

            db1_db2_converter.convert_go_details()
            db1_db2_converter.convert_go_overview()

    GoThread().start()

    pastry_master_converter.convert_bioentity_in_depth()
    pastry_master_converter.convert_bioconcept_in_depth()
    pastry_master_converter.convert_chemical_in_depth()
    master_db1_converter.convert_author_details()
    db1_db2_converter.convert_author_details()
