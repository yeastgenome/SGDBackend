'''
Created on Oct 11, 2013

@author: kpaskov
'''
from convert.converter_interface import ConverterInterface
from convert_perf import convert_core
from convert_perf.convert_data import convert_data
from convert_utils import prepare_schema_connection, check_session_maker, \
    set_up_logging
from model_perf_schema.data import data_classes
from sgdbackend import SGDBackend
import model_perf_schema
import sys

class NexPerfConverter(ConverterInterface):    
    def __init__(self, nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass,
                 perf_dbtype, perf_dbhost, perf_dbname, perf_schema, perf_dbuser, perf_dbpass):
        self.session_maker = prepare_schema_connection(model_perf_schema, perf_dbtype, perf_dbhost, perf_dbname, perf_schema, perf_dbuser, perf_dbpass)
        check_session_maker(self.session_maker, perf_dbhost, perf_schema)
        
        self.backend = SGDBackend(nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass)
        
        from model_perf_schema.core import Bioentity
        self.bioentity_ids = [x.id for x in self.session_maker().query(Bioentity).all()]
        
        self.log = set_up_logging('nex_perf_converter')
            
    def core_wrapper(self, f, chunk_size):
        try:
            f(self.session_maker, self.backend, chunk_size)
        except Exception:
            self.log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
            
    def data_wrapper(self, method_name, obj_ids, chunk_size):
        try:
            convert_data(self.session_maker, data_classes[method_name], getattr(self.backend, method_name), method_name, 'perfconvert.' + method_name, chunk_size)
        except Exception:
            self.log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
    
    def convert_all(self):
        #Core
        self.convert_bioentity()
        self.convert_bioconcept()
        self.convert_reference()
        self.convert_disambig()
        
        #Data
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
        self.convert_regulation_details()
        self.convert_regulation_graph()
        self.convert_regulation_target_enrich()
        
    def convert_daily(self):
        #Core
        self.convert_bioentity()
        self.convert_bioconcept()
        self.convert_reference()
        self.convert_disambig()
        
        #Data
        self.convert_literature_overview()
        self.convert_literature_details()
        self.convert_literature_graph()
        
    def convert_monthly(self):
        #Data
        self.convert_interaction_overview()
        self.convert_interaction_details()
        self.convert_interaction_graph()
        self.convert_interaction_resources()
        
    def convert_updated_flatfiles(self):
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
        self.core_wrapper(convert_core.convert_bioconcept, 10000)
    def convert_reference(self):
        self.core_wrapper(convert_core.convert_reference, 1000)
    def convert_disambig(self):
        self.core_wrapper(convert_core.convert_disambig, 10000)
    def convert_interaction_overview(self):
        self.data_wrapper('interaction_overview', self.bioentity_ids, 1000)
    def convert_interaction_details(self):
        self.data_wrapper('interaction_details', self.bioentity_ids, 1000)
    def convert_interaction_graph(self):
        self.data_wrapper('interaction_graph', self.bioentity_ids, 1000)
    def convert_interaction_resources(self):
        self.data_wrapper('interaction_resources', self.bioentity_ids, 1000)
    def convert_literature_overview(self):    
        self.data_wrapper('literature_overview', self.bioentity_ids, 1000)
    def convert_literature_details(self):
        self.data_wrapper('literature_details', self.bioentity_ids, 1000)
    def convert_literature_graph(self):
        self.data_wrapper('literature_graph', self.bioentity_ids, 1000)
    def convert_protein_domain_details(self):   
        self.data_wrapper('protein_domain_details', self.bioentity_ids, 1000)
    def convert_binding_site_details(self):    
        self.data_wrapper('binding_site_details', self.bioentity_ids, 1000)
    def convert_regulation_overview(self):    
        self.data_wrapper('regulation_overview', self.bioentity_ids, 1000)
    def convert_regulation_details(self):
        self.data_wrapper('regulation_details', self.bioentity_ids, 1000)
    def convert_regulation_graph(self):
        self.data_wrapper('regulation_graph', self.bioentity_ids, 1000)
    def convert_regulation_target_enrich(self):
        self.data_wrapper('regulation_target_enrich', self.bioentity_ids, 100)
        
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
        