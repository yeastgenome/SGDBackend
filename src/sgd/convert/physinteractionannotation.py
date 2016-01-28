from src.sgd.convert import basic_convert

__author__ = 'sweng66'
TAXON_ID = "TAX:4932"

def physinteractionannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.psimod import Psimod

    nex_session = get_nex_session()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    sgdid_to_dbentity_id = dict([(x.sgdid, x.id) for x in nex_session.query(Locus).all()])
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    psimodid_to_psimod_id = dict([(x.psimodid, x.id) for x in nex_session.query(Psimod).all()])

    f = open("src/sgd/convert/data/PSI-MOD2SGD-PTMmapping112115.txt")
    modification_to_psimod_id = {}
    for line in f:
        if line.startswith('BUD'):
            continue
        pieces = line.strip().split('\t')
        if len(pieces) < 5:
            continue
        if pieces[0] == '':
            continue
        psimodid = pieces[4]
        psimod_id = psimodid_to_psimod_id.get(psimodid)
        modification_to_psimod_id[pieces[0]] = psimod_id
        print pieces[0], psimodid, psimod_id
    
    f.close()

    # from: http://www.thebiogrid.org/downloads/datasets/SGD.tab.txt
    f = open("src/sgd/convert/data/SGD.tab.txt")     

    genetic_types = get_genetic_type_list()

    header = True
    for line in f:
        row = line.strip().split('\t')
        if len(row) == 12 and row[4] and row[4] in genetic_types:
            # it is a genetic interaction
            # print "GI: ", line
            continue

        if len(row) == 12: 
            if header:
                header = False
            else:         
                # print "PI: ", line
                reference_id = pmid_to_reference_id.get(int(row[6]))
                if reference_id is None:
                    print "The PMID: ", row[6], " is not in the REFERENCEDBENTITY table."
                    continue

                dbentity1_id = sgdid_to_dbentity_id.get(row[2])
                dbentity2_id = sgdid_to_dbentity_id.get(row[3])
                if dbentity1_id is None:
                    print "The SGDID: ",row[2], " is not in LOCUSDBENTITY table."
                    continue
                if dbentity2_id is None:
                    print "The SGDID: ",row[3], " is not in LOCUSDBENTITY table."
                    continue
            
                annotation_type = 'high-throughput' if 'HTP' in row[9] else 'manually curated'
                    
                obj_json = {
                    'source': {'display_name': 'BioGRID'},
                    'taxonomy_id': taxonomy_id,
                    'reference_id': reference_id,
                    'biogrid_experimental_system': row[4],
                    'annotation_type': annotation_type
                }

                if row[8] != '-' and row[8] != 'No Modification':
                    psimod_id = modification_to_psimod_id.get(row[8])
                    if psimod_id is None:
                        print "The modification term: ", row[8], " is not in PSIMOD table."
                        continue
                    obj_json['psimod_id'] = psimod_id
                    print "MODIFICATION=", row[8], ", PSIMOD_ID=", psimod_id

                # row[11] = vegetative growth

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

                # row[10] = High Throughput: SGA analysis|Low Throughput: Interaction confirmed by random sporulation.             
                if row[10] != '-':
                    obj_json['note'] = row[10]
            
                yield obj_json
                
    f.close()


def get_genetic_type_list():

    return ['Dosage Lethality',
            'Dosage Rescue',
            'Dosage Growth Defect',
            'Epistatic MiniArray Profile',
            'Negative Genetic',
            'Positive Genetic',
            'Phenotypic Enhancement',
            'Phenotypic Suppression',
            'Synthetic Growth Defect',
            'Synthetic Haploinsufficiency',
            'Synthetic Lethality',
            'Synthetic Rescue']

            
def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, physinteractionannotation_starter, 'physinteractionannotation', lambda x: (x['dbentity1_id'], x['dbentity2_id'], x['reference_id'], x['taxonomy_id'], x['bait_hit'], x['biogrid_experimental_system'], x['annotation_type']))



