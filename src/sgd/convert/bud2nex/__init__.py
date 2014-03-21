import sys

from src.sgd.convert.bud2nex import convert_bioentity, convert_phenotype, convert_reference_in_depth
import convert_evelements
import convert_reference
import convert_bioconcept
import convert_bioitem
import convert_chemical
import convert_literature
import convert_go
import convert_qualifier
import convert_interaction
import convert_binding
import convert_protein_domain
import convert_regulation
import convert_complex
import convert_sequence
import convert_phosphorylation
import convert_bioentity_in_depth
import convert_bioconcept_in_depth
import convert_chemical_in_depth
import convert_bioitem_in_depth
import convert_ec_number
import convert_protein_experiment
from src.sgd.model import bud, nex
from src.sgd.convert import ConverterInterface, config, prepare_schema_connection, check_session_maker, set_up_logging

__author__ = 'kpaskov'

class BudNexConverter(ConverterInterface):
    def __init__(self, bud_dbtype, bud_dbhost, bud_dbname, bud_schema, bud_dbuser, bud_dbpass,
                        nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass):
        self.old_session_maker = prepare_schema_connection(bud, bud_dbtype, bud_dbhost, bud_dbname, bud_schema, bud_dbuser, bud_dbpass)
        check_session_maker(self.old_session_maker, bud_dbhost, bud_schema)

        self.new_session_maker = prepare_schema_connection(nex, nex_dbtype, nex_dbhost, nex_dbname, nex_schema, nex_dbuser, nex_dbpass)
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

    def convert_basic(self):
        self.wrapper(convert_evelements.convert)
        self.wrapper(convert_reference.convert)
        self.wrapper(convert_bioentity.convert)
        self.wrapper(convert_bioconcept.convert)
        self.wrapper(convert_bioitem.convert)
        self.wrapper(convert_chemical.convert)
        self.wrapper(convert_qualifier.convert)

    def convert_basic_continued(self):
        self.wrapper(convert_bioentity_in_depth.convert)
        self.wrapper(convert_bioconcept_in_depth.convert)
        self.wrapper(convert_chemical_in_depth.convert)
        self.wrapper(convert_bioitem_in_depth.convert, no_old_session=True)

    def convert_reference(self):
        self.wrapper(convert_reference_in_depth.convert)

    def convert_phenotype(self):
        self.wrapper(convert_phenotype.convert)

    def convert_literature(self):
        self.wrapper(convert_literature.convert)

    def convert_go(self):
        self.wrapper(convert_go.convert)

    def convert_ec_number(self):
        self.wrapper(convert_ec_number.convert)

    def convert_complex(self):
        self.wrapper(convert_complex.convert, no_old_session=True)

    def convert_sequence(self):
        self.wrapper(convert_sequence.convert)
        self.wrapper(convert_phosphorylation.convert, no_old_session=True)

    def convert_interaction(self):
        self.wrapper(convert_interaction.convert)

    def convert_protein(self):
        self.wrapper(convert_protein_domain.convert)
        self.wrapper(convert_binding.convert, no_old_session=True)
        self.wrapper(convert_protein_experiment.convert)

    def convert_regulation(self):
        self.wrapper(convert_regulation.convert, no_old_session=True)

if __name__ == "__main__":

    if len(sys.argv) == 4:
        bud_dbhost = sys.argv[1]
        nex_dbhost = sys.argv[2]
        method = sys.argv[3]
        converter = BudNexConverter(config.BUD_DBTYPE, bud_dbhost, config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS,
                                    config.NEX_DBTYPE, nex_dbhost, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
        getattr(converter, method)()
    else:
        print 'Please enter bud_dbhost, nex_dbhost, and method.'
