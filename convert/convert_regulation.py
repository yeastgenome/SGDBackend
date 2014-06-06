'''
Created on Oct 24, 2013

@author: kpaskov
'''
from convert import config
from convert.bud_nex_converter import BudNexConverter
from convert.nex_perf_converter import NexPerfConverter
from convert.perf_perf_converter import PerfPerfConverter

if __name__ == "__main__":   
    pastry_master_converter = BudNexConverter(config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS,
                                    config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    pastry_master_converter.convert_regulation()

    master_db1_converter = NexPerfConverter(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS,
                                    config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    master_db1_converter.load_ids()

    #master_db1_converter.convert_regulation_overview()
    master_db1_converter.convert_regulation_details()
    #master_db1_converter.convert_regulation_graph()
    #master_db1_converter.convert_regulation_target_enrich()
    #master_db1_converter.convert_regulation_paragraph()

    db1_db2_converter = PerfPerfConverter(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS,
                                    config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    db1_db2_converter.load_ids()

    #db1_db2_converter.convert_regulation_overview()
    db1_db2_converter.convert_regulation_details()
    #db1_db2_converter.convert_regulation_graph()
    #db1_db2_converter.convert_regulation_target_enrich()
    #db1_db2_converter.convert_regulation_paragraph()
