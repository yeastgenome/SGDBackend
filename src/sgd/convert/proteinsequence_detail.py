from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_strain_taxid_mapping


__author__ = 'sweng66'

def proteinsequence_detail_starter(bud_session_maker):

    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.contig import Contig
    from src.sgd.model.nex.proteinsequenceannotation import Proteinsequenceannotation
        
    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    locus_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    contig_name_to_contig_id = dict([(x.display_name, x.id) for x in nex_session.query(Contig).all()])
    key_to_annotation_id =  dict([((x.dbentity_id, x.taxonomy_id), x.id) for x in nex_session.query(Proteinsequenceannotation).all()])
    key2_to_annotation_id =  dict([((x.dbentity_id, x.taxonomy_id, x.contig_id), x.id) for x in nex_session.query(Proteinsequenceannotation).all()])

    strain_to_taxid_mapping = get_strain_taxid_mapping()
    
    files = ['src/sgd/convert/data/protparam_s288c.txt',
             'src/sgd/convert/data/protparam_strains.txt']

    for file in files:
        f = open(file, 'r')
        for line in f:
            ppdata = line.split("\t")
            name = ppdata[0]
            strain = None
            contig = None
            if "_" in ppdata[0]:
                [name, strain, contig] = ppdata[0].split('_')
            if name.startswith('UNDEF') or name.startswith('ORF'):
                continue
            
            dbentity_id = locus_to_dbentity_id.get(name)
            if dbentity_id is None:
                print "The feature_name =", name, " is not in the LOCUSDBENTITY table."
                continue
            if strain is None:
                strain = 'S288C'
            elif strain == 'CEN.PK2-1Ca':
                strain = 'CENPK'
            elif strain.startswith('Sigma'):
                strain = 'Sigma1278b'
            elif strain.startswith('RM11-1'):
                strain = 'RM11-1a'
            taxid = strain_to_taxid_mapping.get(strain)
            if taxid is None:
                print "The strain: ", strain, " is not mapped to a TAXON ID."
                continue
            taxonomy_id = taxid_to_taxonomy_id.get(taxid)
            if taxonomy_id is None:
                print "The taxon ID:", taxid, " is not in TAXONOMY table."
                continue
            contig_id = None
            if strain != 'S288C' and contig is None:
                print "No contig name for entry: ", line
                continue
            if contig is not None:
                contig_id = contig_name_to_contig_id.get(contig)
                if contig_id is None:
                    print "The contig name: ", contig, " is not in Contig table."
                    continue
            annotation_id = None
            if strain == 'S288C':
                annotation_id = key_to_annotation_id.get((dbentity_id, taxonomy_id))
            else:
                annotation_id = key2_to_annotation_id.get((dbentity_id, taxonomy_id, contig_id))
            if annotation_id is None:
                print "The dbentity_id for ", name, " and taxonomy_id for ", strain, " entry is not in the PROTEINSEQUENCEANNOTATION table."
                continue

            carbon = None
            hydrogen = None
            nitrogen = None
            oxygen = None
            sulfur = None
            try:
                carbon = int(ppdata[31])
                hydrogen = int(ppdata[32])
                nitrogen = int(ppdata[33])
                oxygen = int(ppdata[34])
                sulfur = int(ppdata[35])
            except:
                print 'Trouble with protparam: ' + str(ppdata)
 
            yield { "annotation_id": annotation_id,
                    "molecular_weight": float(ppdata[1]),
                    "pi": float(ppdata[2]),
                    "protein_length": int(ppdata[3]),
                    'n_term_seq': ppdata[4],
                    'c_term_seq': ppdata[5],
                    "gravy_score": float(ppdata[6]),      
                    "aromaticity_score": float(ppdata[7]),
                    "cai": float(ppdata[8]),
                    "codon_bias": float(ppdata[9]), 
                    "fop_score": float(ppdata[10]),   
                    "ala": int(ppdata[11]),
                    "cys": int(ppdata[12]),
                    "asp": int(ppdata[13]),
                    "glu": int(ppdata[14]),
                    "phe": int(ppdata[15]),
                    "gly": int(ppdata[16]),
                    "his": int(ppdata[17]),
                    "ile": int(ppdata[18]),
                    "lys": int(ppdata[19]),
                    "leu": int(ppdata[20]),
                    "met": int(ppdata[21]),
                    "asn": int(ppdata[22]),
                    "pro": int(ppdata[23]),
                    "gln": int(ppdata[24]),
                    "arg": int(ppdata[25]),
                    "ser": int(ppdata[26]),
                    "thr": int(ppdata[27]),
                    "val": int(ppdata[28]),
                    "trp": int(ppdata[29]),
                    "tyr": int(ppdata[30]),
                    "carbon": carbon,
                    "hydrogen": hydrogen,
                    "nitrogen": nitrogen,
                    "oxygen": oxygen,
                    "sulfur": sulfur,
                    "instability_index": float(ppdata[36]),                  
                    "all_cys_ext_coeff": float(ppdata[37]),
                    "no_cys_ext_coeff": float(ppdata[38]),        
                    "aliphatic_index": float(ppdata[39].strip()) }

        f.close()

    nex_session.close()
    bud_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, proteinsequence_detail_starter, 'proteinsequence_detail', lambda x: (x['annotation_id'], x['molecular_weight'], x['protein_length'], x['n_term_seq'], x['c_term_seq']))
