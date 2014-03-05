'''
Created on Oct 11, 2013

@author: kpaskov
'''
import sys

from convert.converter_interface import ConverterInterface
from convert_core import convert_evelements, convert_reference, \
    convert_bioentity, convert_bioconcept, convert_bioitem, convert_chemical
from convert_evidence import convert_literature, convert_go, convert_qualifier, \
    convert_interaction, convert_binding, convert_protein_domain, convert_regulation, \
    convert_phenotype, convert_complex, convert_sequence, convert_phosphorylation
from convert_other import convert_bioentity_in_depth, convert_reference_in_depth, \
    convert_bioconcept_in_depth, convert_chemical_in_depth, convert_bioitem_in_depth
from convert_utils import prepare_schema_connection, check_session_maker, \
    set_up_logging
import model_new_schema
import model_old_schema


class BudNexConverter(ConverterInterface):    
    def __init__(self, bud_dbtype, bud_dbhost, bud_dbname, bud_schema, bud_dbuser, bud_dbpass,
                        nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass):
        self.old_session_maker = prepare_schema_connection(model_old_schema, bud_dbtype, bud_dbhost, bud_dbname, bud_schema, bud_dbuser, bud_dbpass)
        check_session_maker(self.old_session_maker, bud_dbhost, bud_schema)
            
        self.new_session_maker = prepare_schema_connection(model_new_schema, nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass)
        check_session_maker(self.new_session_maker, nex_dbhost, nex_schema)
            
        self.log = set_up_logging('bud_nex_converter')
            
    def wrapper(self, f, no_old_session=False):
        try:
            if not no_old_session:
                f(self.old_session_maker, self.new_session_maker)
            else:
                f(self.new_session_maker)
        except Exception:
            self.log.exception( "Unexpected error:" + str(sys.exc_info()[0]) )
            
    def convert_core(self):
        self.convert_evelements()
        self.convert_reference()
        self.convert_bioentity()
        self.convert_bioconcept()
        self.convert_bioitem()
        self.convert_chemical()
    
    def convert_all(self):
        #Core
        self.convert_core()
    
        #Evidence
        self.convert_phenotype()
        self.convert_literature()
        self.convert_go()
        self.convert_qualifier()
        self.convert_interaction()
        self.convert_binding()
        self.convert_protein_domain()
        self.convert_regulation()
        
        #Other
        self.convert_bioentity_in_depth()
        self.convert_reference_in_depth()
        self.convert_bioconcept_in_depth()
        self.convert_chemical_in_depth()
        
    def convert_daily(self):
        #Core
        self.convert_core()
    
        #Evidence
        self.convert_phenotype()
        self.convert_literature()
        self.convert_go()
        self.convert_qualifier()
        
        #Other
        self.convert_bioentity_in_depth()
        self.convert_reference_in_depth()
        self.convert_bioconcept_in_depth()
        self.convert_bioitem_in_depth()
        self.convert_chemical_in_depth()
        
    def convert_monthly(self):
        #Evidence
        self.convert_interaction() 
        
    def convert_updated_flatfiles(self):
        #Evidence
        self.convert_binding()
        self.convert_protein_domain()
        self.convert_regulation()
        
    def convert_evelements(self):
        self.wrapper(convert_evelements.convert)
    def convert_reference(self):
        self.wrapper(convert_reference.convert)
    def convert_bioentity(self):
        self.wrapper(convert_bioentity.convert)
    def convert_bioconcept(self):
        self.wrapper(convert_bioconcept.convert)
    def convert_bioitem(self):
        self.wrapper(convert_bioitem.convert)
    def convert_chemical(self):
        self.wrapper(convert_chemical.convert)
    def convert_phenotype(self):
        self.wrapper(convert_phenotype.convert)
    def convert_literature(self):
        self.wrapper(convert_literature.convert)
    def convert_go(self):
        self.wrapper(convert_go.convert)
    def convert_qualifier(self):
        self.wrapper(convert_qualifier.convert)
    def convert_complex(self):
        self.wrapper(convert_complex.convert, no_old_session=True)
    def convert_sequence(self):
        self.wrapper(convert_sequence.convert)
    def convert_interaction(self):
        self.wrapper(convert_interaction.convert)
    def convert_binding(self):
        self.wrapper(convert_binding.convert, no_old_session=True)
    def convert_protein_domain(self):
        self.wrapper(convert_protein_domain.convert)
    def convert_regulation(self):
        self.wrapper(convert_regulation.convert, no_old_session=True)
    def convert_phosphorylation(self):
        self.wrapper(convert_phosphorylation.convert, no_old_session=True)
    def convert_bioentity_in_depth(self):
        self.wrapper(convert_bioentity_in_depth.convert)
    def convert_reference_in_depth(self):
        self.wrapper(convert_reference_in_depth.convert)
    def convert_bioconcept_in_depth(self):
        self.wrapper(convert_bioconcept_in_depth.convert)
    def convert_chemical_in_depth(self):
        self.wrapper(convert_chemical_in_depth.convert)
    def convert_bioitem_in_depth(self):
        self.wrapper(convert_bioitem_in_depth.convert, no_old_session=True)
        
if __name__ == "__main__":
    from convert import config
    
    if len(sys.argv) == 4:
        bud_dbhost = sys.argv[1]
        nex_dbhost = sys.argv[2]
        method = sys.argv[3]
        converter = BudNexConverter(config.BUD_DBTYPE, bud_dbhost, config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS, 
                                    config.NEX_DBTYPE, nex_dbhost, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
        getattr(converter, method)()
    else:
        print 'Please enter bud_dbhost, nex_dbhost, and method.'
