from src.sgd.convert import basic_convert

__author__ = 'sweng66'
TAXON_ID = "TAX:4932"

def geninteractionannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.phenotype import Phenotype

    nex_session = get_nex_session()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    sgdid_to_dbentity_id = dict([(x.sgdid, x.id) for x in nex_session.query(Locus).all()])
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    phenotype_to_phenotype_id = dict([(x.display_name, x.id) for x in nex_session.query(Phenotype).all()])

    genetic_type_to_phenotype = get_genetic_type_to_pheno_mapping()
    old_to_new_phenotype = get_old_to_new_pheno_mapping()

    # from: http://www.thebiogrid.org/downloads/datasets/SGD.tab.txt
    f = open("src/sgd/convert/data/SGD.tab.txt")     

    genetic_type = {}
    header = True
    for line in f:
        row = line.strip().split('\t')
        if len(row) < 12 or genetic_type_to_phenotype.get(row[4]) == None:
            continue
        if len(row) == 12: 
            if header:
                header = False
            else:
                oldPheno = genetic_type_to_phenotype.get(row[4])          
                newPheno = old_to_new_phenotype.get(oldPheno)
                
                reference_id = pmid_to_reference_id.get(int(row[6]))
                if reference_id is None:
                    print "The PMID: ", row[6], " is not in the REFERENCEDBENTITY table."
                    continue

                annotation_type = 'high-throughput' if 'HTP' in row[9] else 'manually curated'

                obj_json = {
                    'source': {'display_name': 'BioGRID'},
                    'taxonomy_id': taxonomy_id,
                    'reference_id': reference_id,
                    'biogrid_experimental_system': row[4],
                    'annotation_type': annotation_type
                }

                dbentity1_id = sgdid_to_dbentity_id.get(row[2])
                dbentity2_id = sgdid_to_dbentity_id.get(row[3])
                if dbentity1_id is None:
                    print "The SGDID: ", row[2], " is not in the LOCUSDBENTITY table."
                    continue
                if dbentity2_id is None:
                    print "The SGDID: ", row[3], " is not in the LOCUSDBENTITY table."
                    continue

                id1 = int(row[2].lstrip("S").lstrip("0"))
                id2 = int(row[3].lstrip("S").lstrip("0"))
                if id1 < id2:
                    obj_json['dbentity1_id'] = dbentity1_id
                    obj_json['dbentity2_id'] = dbentity2_id
                    obj_json['bait_hit'] = 'Bait-Hit'
                else:
                    obj_json['dbentity1_id'] = dbentity2_id
                    obj_json['dbentity2_id'] = dbentity1_id
                    obj_json['bait_hit'] = 'Hit-Bait'
                
                if row[10] != '-':
                    obj_json['note'] = row[10]
                                   
                if newPheno is not None:
                    phenotype_id = phenotype_to_phenotype_id.get(newPheno)
                    if phenotype_id is None:
                        print "The phenotype: ", newPheno, " is not in the Phenotype table."
                    else:
                        obj_json['phenotype_id'] = phenotype_id
                else:
                    print "The phenotype: ", oldPheno, " can not be mapped to a new one."
            
                yield obj_json

    f.close()


def get_genetic_type_to_pheno_mapping():

    return {'Dosage Lethality'               : 'inviable',
            'Dosage Rescue'                  : 'wildtype',
            'Dosage Growth Defect'           : 'slow growth',
            'Epistatic MiniArray Profile'    : 'Not available',
            'Negative Genetic'               : 'Not available',
            'Positive Genetic'               : 'Not available',
            'Phenotypic Enhancement'         : 'Not available',
            'Phenotypic Suppression'         : 'Not available',
            'Synthetic Growth Defect'        : 'slow growth',
            'Synthetic Haploinsufficiency'   : 'Not available',
            'Synthetic Lethality'            : 'inviable',
            'Synthetic Rescue'               : 'wildtype'}


def get_old_to_new_pheno_mapping():

    return { 'inviable'    : 'inviable',
             'slow growth' : 'vegetative growth: decreased',
             'wildtype'    : 'vegetative growth: normal' }
 

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, geninteractionannotation_starter, 'geninteractionannotation', lambda x: (x['dbentity1_id'], x['dbentity2_id'], x['reference_id'], x['taxonomy_id'], x.get('phenotype_id'), x['bait_hit'], x['biogrid_experimental_system'], x['annotation_type']))




