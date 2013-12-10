'''
Created on Oct 24, 2013

@author: kpaskov
'''

from convert import config
from convert.bud_nex_converter import BudNexConverter
from convert.nex_perf_converter import NexPerfConverter

if __name__ == "__main__":   
    #Pastry -> Dev_nex
    pastry_dev_converter = BudNexConverter(config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS, 
                                    config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    #pastry_dev_converter.convert_chemical()
    #pastry_dev_converter.convert_chemical()
    #pastry_dev_converter.convert_phenotype()
    #pastry_dev_converter.convert_bioconcept()
    #pastry_dev_converter.convert_bioconcept_in_depth()
    #pastry_dev_converter.convert_phenotype()
    #pastry_dev_converter.convert_evelements()
    #pastry_dev_converter.convert_reference()
    pastry_dev_converter.convert_bioentity_in_depth()

    #Dev_nex -> Dev_perf
    #dev_perf_converter = NexPerfConverter(config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, 
    #                                 config.PERF_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
    