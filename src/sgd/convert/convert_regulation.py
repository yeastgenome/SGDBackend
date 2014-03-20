from src.sgd.convert import config
from src.sgd.convert.bud2nex import BudNexConverter
from src.sgd.convert.nex2perf import NexPerfConverter
from src.sgd.convert.perf2perf import PerfPerfConverter

__author__ = 'kpaskov'

if __name__ == "__main__":   
    pastry_master_converter = BudNexConverter(config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS, 
                                    config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    
    master_db1_converter = NexPerfConverter(config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, 
                                     config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    db1_db2_converter = PerfPerfConverter(config.PERF_DBTYPE, 'sgd-db1.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS, 
                                     config.PERF_DBTYPE, 'sgd-db2.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

    pastry_master_converter.convert_regulation()
    master_db1_converter.convert_regulation()
    db1_db2_converter.convert_regulation()
