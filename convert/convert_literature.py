'''
Created on Oct 24, 2013

@author: kpaskov
'''

from convert import config
from convert.bud_nex_converter import BudNexConverter
from convert.nex_perf_converter import NexPerfConverter
from convert.perf_perf_converter import PerfPerfConverter

if __name__ == "__main__":   
    #Pastry -> Master
    pastry_master_converter = BudNexConverter(config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS,
                                    config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    #Master -> DB1
    master_db1_converter = NexPerfConverter(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS,
                                     config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    master_db1_converter.load_ids()

    #DB1 -> DB2
    db1_db2_converter = PerfPerfConverter(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS,
                                     config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    db1_db2_converter.load_ids()

    pastry_master_converter.convert_literature()

    master_db1_converter.convert_literature_overview()
    master_db1_converter.convert_literature_details()
    master_db1_converter.convert_literature_graph()

    db1_db2_converter.convert_literature_overview()
    db1_db2_converter.convert_literature_details()
    db1_db2_converter.convert_literature_graph()

