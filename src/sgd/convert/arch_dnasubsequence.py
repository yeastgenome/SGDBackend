from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert
from src.sgd.convert.util import number_to_roman

__author__ = 'sweng66'

S288C_TAXON = "TAX:559292"

def arch_dnasubsequence_starter(bud_session_maker):
    from src.sgd.model.nex.so import So
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.arch_contig import ArchContig
    from src.sgd.model.nex.arch_dnaseqannotation import ArchDnaseqannotation
    from src.sgd.model.nex.genomerelease import Genomerelease

    nex_session = get_nex_session()
    
    format_name_to_contig_id = dict([(x.format_name, x.id) for x in nex_session.query(ArchContig).all()])    
    type_to_so_id = dict([(x.display_name, x.id) for x in nex_session.query(So).all()]) 
    feature_bud_id_to_dbentity_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    contig_id_dbentity_id_to_annotation = dict([((x.contig_id, x.dbentity_id), x) for x in nex_session.query(ArchDnaseqannotation).all()])
    genomerelease_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Genomerelease).all()])
                                    
    S288C_taxonomy_obj = nex_session.query(Taxonomy).filter_by(taxid=S288C_TAXON).first()
    S288C_taxonomy_id = S288C_taxonomy_obj.id

    feature_types = get_feature_type_list()

    # 1.  Version = 64-1-1
    # 2.  Chromosome = VI
    # 3.  parent_feature = YFL039C
    # 4.  parent_feature_no = 4430
    # 5.  parent_gene_name = ACT1
    # 6.  child_feature =YFL039C_14914
    # 7.  child_feature_no = 13531
    # 8.  child_feature_type = CDS
    # 9.  seq_version
    # 10. coord_version
    # 11. min_coord
    # 12. max_coord
    # 13. created_by
    # 14. date_created
    # 15. residues

    f = open("src/sgd/convert/data/arch_dnasubsequence.txt")
    for line in f:
        pieces = line.strip().split("\t")
        if len(pieces) < 15:
            print "bad row: ", line 
            continue
        if pieces[8] is None or pieces[9] is None or pieces[10] == 0 or pieces[11] == 0 or pieces[12] == '':
            continue
        if pieces[7] not in feature_types:
            continue
        so_id = type_to_so_id.get(pieces[7])
        if so_id is None:
            print "The feature_type:", pieces[7], " is not in SO table."
            continue
        genome_release = pieces[0]
        arch_contig_format_name = None
        if pieces[1] == 17:
            arch_contig_format_name = "Chromosome_Mito_R" + genome_release
        elif pieces[1] == '2-micron':
            arch_contig_format_name = "2-micron_plasmid_R" + genome_release
        else:
            arch_contig_format_name = "Chromosome_" + number_to_roman[pieces[1]]+ "_R" + genome_release
        arch_contig_id = format_name_to_contig_id.get(arch_contig_format_name)
        if arch_contig_id is None:
            print "The contig format_name: ", arch_contig_format_name, " is not in ARCH_CONTIG table."
            continue
        parent_dbentity_id = feature_bud_id_to_dbentity_id.get(int(pieces[3]))
        ## eg dbentity_id for ACT1
        if parent_dbentity_id is None:
            print "The feature_no: ", pieces[3], " is not in LOCUSDBENTITY table."
            continue
        annotation = contig_id_dbentity_id_to_annotation.get((arch_contig_id, parent_dbentity_id))
        if annotation is None:
            print "The contig_id =", arch_contig_id, " and dbentity_is =", parent_dbentity_id, " is not in ARCH_DNASEQANNOTATION table."                                    
            continue
        annotation_id = annotation.id
        genomerelease_id = genomerelease_to_id.get(genome_release)
        if genomerelease_id is None:
            print "The genomerelease: ", genome_release, " is not in GENOMERELEASE table."
            continue
        dbentity_id = feature_bud_id_to_dbentity_id.get(int(pieces[6]))                           
        if dbentity_id is None:
            print "The BUD_ID = feature_no =", pieces[6], " is not in LOCUSDBENTITY table."
            continue

        start = int(pieces[10])
        end = int(pieces[11])
        display_name = pieces[7]
        relative_start_index = start - annotation.start_index + 1
        relative_end_index = end - annotation.start_index + 1
        contig_start_index = start
        contig_end_index = end
        parent_name = pieces[2]
        parent_gene = pieces[4]
        if parent_gene == "":
            parent_gene = parent_name
        file_header = ">" + parent_name + " " + parent_gene + " " + pieces[7] + ":" + str(start) + ".." + str(end) 
        download_filename = parent_name + "_" + pieces[7] + ".fsa"

        yield { 'annotation_id': annotation_id,
                'dbentity_id': dbentity_id,
                'display_name': display_name,
                'genomerelease_id': genomerelease_id,
                'so_id': so_id,
                'relative_start_index': relative_start_index,
                'relative_end_index': relative_end_index,
                'contig_start_index': contig_start_index,
                'contig_end_index': contig_end_index,
                'seq_version': str(pieces[8]),
                'coord_version': str(pieces[9]),
                'created_by': pieces[12],
                'date_created': str(pieces[13]),
                'residues': pieces[14],
                'file_header': file_header,
                'download_filename': download_filename }
    
    f.close()
    nex_session.close()
    

def get_feature_type_list():

    return [ "ARS_consensus_sequence",
             "CDS",
             "W_region",
             "X_element",
             "X_element_combinatorial_repeat",
             "X_region",
             "Y_prime_element",
             "Y_region",
             "Z1_region",
             "Z2_region",
             "binding_site",
             "centromere_DNA_Element_I",
             "centromere_DNA_Element_II",
             "centromere_DNA_Element_III",
             "external_transcribed_spacer_region",
             "five_prime_UTR_intron",
             "insertion",
             "intein_encoding_region",
             "internal_transcribed_spacer_region",
             "intron",
             "mRNA",
             "non_transcribed_region",
             "noncoding_exon",
             "plus_1_translational_frameshift",
             "telomeric_repeat",
             "uORF" ]

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, arch_dnasubsequence_starter, 'arch_dnasubsequence', lambda x: (x['annotation_id'], x['dbentity_id'], x['so_id'], x['residues'], x['relative_start_index'], x['relative_end_index']))
