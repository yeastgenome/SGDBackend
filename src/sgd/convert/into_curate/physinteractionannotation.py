from src.sgd.convert.into_curate import basic_convert
from sqlalchemy.sql.expression import or_
from interaction_config import genetic_type_to_phenotype, old_phenotype_to_new_phenotype
import urllib
import shutil
import filecmp
import os.path
import sys

__author__ = 'sweng66'

def physinteractionannotation_starter(bud_session_maker):

    header = True

    # biogrid_file = sys.argv[1]
 
    biogrid_file = "SGD.tab.txt"

    f = open(biogrid_file)     

    for line in f:

        row = line.strip().split('\t')
    
        if len(row) == 12 and row[4] and row[4] in genetic_type_to_phenotype:
            # it is genetic interaction
            print "GI: ", line
            continue

        if len(row) == 12: 
            if header:
                header = False
            else:         
                print "PI: ", line                
                obj_json = {
                    'source': {'name': 'BioGRID'},
                    'taxonomy': {'name': 'Saccharomyces cerevisiae S288c', 
                                 'ncbi_taxon_id': 559292 },
                    'reference': {'pubmed_id': int(row[6])},
                    'modification': row[8],
                    'annotation_type': row[9]
                }
                
                ## check syntax
                id1 = row[2].replace("S0+", "")
                id2 = row[3].replace("S0+", "")
                if id_1 < id_2:
                    obj_json['dbentity1'] = {'sgdid': row[2]}
                    obj_json['dbentity2'] = {'sgdid': row[3]}
                    obj_json['bait_hit'] = 'bait-hit'
                else:
                    obj_json['dbentity1'] = {'sgdid': row[3]}
                    obj_json['dbentity2'] = {'sgdid': row[2]}
                    obj_json['bait_hit'] = 'hit-bait'

                if row[10] != '-':
                    obj_json['note'] = row[10]
            
                yield obj_json
                
    f.close()

def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, physinteractionannotation_starter, 'physinteractionannotation', lambda x: (x['dbentity1']['sgdid'], x['dbentity2']['sgdid'], x['reference']['pubmed_id'], x['modification'], x['annotation_type']))


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

