from src.sgd.convert import basic_convert
from src.sgd.convert.sequence_files import sequence_files, new_sequence_files
from src.sgd.convert.util import make_fasta_file_starter, number_to_roman, get_sequence_library_fsa, get_strain_taxid_mapping

__author__ = 'sweng66'

def dnasequenceannotation_starter(bud_session_maker):

    from src.sgd.model.nex.strain import Strain
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.so import So
    from src.sgd.model.nex.contig import Contig
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.genomerelease import Genomerelease

    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    # strain_to_strain_id =  dict([(x.format_name, x.id) for x in nex_session.query(Strain).all()])
    contig_to_contig_id = dict([(x.format_name, x.id) for x in nex_session.query(Contig).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])

    genomerelease_to_genomerelease_id =  dict([(x.display_name, x.id) for x in nex_session.query(Genomerelease).all()])

    type_to_so_id = dict([(x.display_name, x.id) for x in nex_session.query(So).all()]) 

    locus_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])

    strain_to_taxid_mapping = get_strain_taxid_mapping()

    #load genomic sequences for S288C  

    from sqlalchemy.sql.expression import or_
    from src.sgd.model.bud.feature import Feature, FeatRel
    from src.sgd.model.bud.sequence import Sequence, Feat_Location

    feature_types = get_feature_type_list()

    taxid = strain_to_taxid_mapping['S288C']
    taxonomy_id = taxid_to_taxonomy_id[taxid]

    bud_id_to_contig_id = dict()
    bud_id_to_chr = dict()

    print "Getting data from BUD..."

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    child_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in bud_session.query(FeatRel).filter_by(rank=1).all()])

    id_to_feature = dict([(x.id, x) for x in bud_session.query(Feature).all()])

    for bud_id in child_id_to_parent_id: 
        ## bud_id = child_id; chr_id = parent_id
        chr_id = child_id_to_parent_id[bud_id]
        if id_to_feature[chr_id].name in number_to_roman:
            chr_name = 'Chromosome_' + number_to_roman[id_to_feature[chr_id].name] 
            bud_id_to_chr[bud_id] = number_to_roman[id_to_feature[chr_id].name]
        elif id_to_feature[chr_id].name == '2-micron':
            chr_name = '2-mircon_plasmid'
            bud_id_to_chr[bud_id] = '2-mircon_plasmid'
        else:
            chr_name = 'Chromosome_' + id_to_feature[bud_id].name
            bud_id_to_chr[bud_id] = id_to_feature[bud_id].name
        if chr_name in contig_to_contig_id:
            bud_id_to_contig_id[bud_id] = contig_to_contig_id[chr_name]

    name_to_so_id = dict()
    name_to_dbentity_id = dict()
    name_to_contig_id = dict()
    name_to_start = dict()
    name_to_end = dict()
    name_to_strand = dict()
    name_to_seq_version = dict()
    name_to_coord_version = dict()
    name_to_date_created = dict()
    name_to_created_by = dict()

    for bud_location in bud_session.query(Feat_Location).all():
        bud_id = bud_location.feature_id                                   
         
        type = id_to_feature[bud_id].type  
        if type in feature_types and bud_location.is_current == 'Y':
            name = id_to_feature[bud_id].name
            gene_name = id_to_feature[bud_id].gene_name
            sgdid = id_to_feature[bud_id].dbxref_id
            chr = bud_id_to_chr[bud_id]    

            dbentity_id = bud_id_to_locus_id.get(bud_id)
            if dbentity_id is None:
                print "The feature ", name, " is not in DBENTITY table."
                continue

            contig_id = bud_id_to_contig_id.get(bud_id)
            if contig_id is None:
                print "The feature ", name, " is not mapped to a chromosome."
                continue

            so_id = type_to_so_id.get(type)
            if so_id is None:
                print "The feature_type ", type, " is not in SO table."
                continue

            name_to_dbentity_id[name] = dbentity_id
            name_to_contig_id[name] = contig_id
            name_to_so_id[name] = so_id
            name_to_start[name] = bud_location.min_coord
            name_to_end[name] = bud_location.max_coord
            name_to_strand[name] = bud_location.strand
            name_to_seq_version[name] = str(bud_location.sequence.seq_version)
            name_to_coord_version[name] = str(bud_location.coord_version)
            name_to_date_created[name] = str(bud_location.sequence.date_created)
            name_to_created_by[name] = str(bud_location.sequence.created_by)

            ## genomic sequence example fasta header
            ## >YAL005C SSA1 SGDID:S000000004 Chr I from 141431-139503, Genome Release 64-2-1
            if gene_name is None:
                gene_name = ''
            file_header = name + " " + gene_name + " SGDID:" + sgdid + " Chr " + chr + " from "
            if bud_location.strand == '-':
                file_header = file_header + str(bud_location.max_coord) + "-" + str(bud_location.min_coord)
            else:
                file_header = file_header + str(bud_location.min_coord) + "-" + str(bud_location.max_coord)
            file_header = file_header + ", Genome Release 64-2-1"
            ## filename: YAL005C-genomic.fsa
            download_filename = name + "-genomic.fsa"

            yield { 'source': { "display_name": 'SGD'},
                    'taxonomy_id': taxonomy_id,
                    'dbentity_id': bud_id_to_locus_id[bud_id],
                    'dna_type': 'GENOMIC',
                    'so_id': so_id,
                    'residues': bud_location.sequence.residues,
                    'seq_version': str(bud_location.sequence.seq_version),
                    'coord_version': str(bud_location.coord_version),
                    'bud_id': bud_location.sequence.id,
                    'contig_id': contig_id,
                    'start_index': bud_location.min_coord,
                    'end_index': bud_location.max_coord,
                    'strand': bud_location.strand,
                    'file_header': file_header,
                    'download_filename': download_filename,
                    'date_created': str(bud_location.sequence.date_created),
                    'created_by': bud_location.sequence.created_by }

    ## load coding sequences for S288C

    coding_sequence_files = [ 'src/sgd/convert/data/strains/orf_coding_all.fasta',
                              'src/sgd/convert/data/strains/rna_coding.fasta']

    # >YAL001C TFC3 SGDID:S000000001, Chr I from 151006-147594,151166-151097, Genome Release 64-2-1, reverse complement, intron sequence removed, Verified ORF, "Subunit of RNA polymerase III transcription initiation factor complex; part of the TauB domain of TFIIIC that binds DNA at the BoxB promoter sites of tRNA and similar genes; cooperates with Tfc6p in DNA binding; largest of six subunits of the RNA polymerase III transcription initiation factor complex (TFIIIC)"

    # >HRA1 HRA1 SGDID:S000119380, Chr I from 99305-99868, Genome Release 64-2-1, ncRNA_gene, "Non-protein-coding RNA; substrate of RNase P, possibly involved in rRNA processing, specifically maturation of 20S precursor into the mature 18S rRNA"

    for seqfile in coding_sequence_files:
        f = open(seqfile, 'r')
        for name, (file_header, residues) in get_sequence_library_fsa(f).iteritems():
            if name == 'tS(GCU)L':
                name = 'tX(XXX)L'
            elif name == 'tT(XXX)Q2':
                name = 'tT(UAG)Q2'
            download_filename = name + '-coding.fsa'
            dbentity_id = locus_to_dbentity_id.get(name)
            if dbentity_id is None:
                print "The feature ", name, " is not in DBENTITY table."
                continue

            yield { 'source': { "display_name": 'SGD'},
                    'taxonomy_id': taxonomy_id,
                    'dbentity_id': name_to_dbentity_id[name],
                    'dna_type': 'CODING',
                    'so_id': name_to_so_id[name],
                    'residues': residues,
                    'seq_version': name_to_seq_version[name],
                    'coord_version': name_to_coord_version[name],
                    'contig_id': name_to_contig_id[name],
                    'start_index': name_to_start[name],
                    'end_index': name_to_end[name],
                    'strand': name_to_strand[name],
                    'file_header': file_header,
                    'download_filename': download_filename,
                    'date_created': name_to_date_created[name],
                    'created_by': name_to_created_by[name]} 

        f.close()


    ### load genomic_1k sequences for S288C

    genomic_1k_files = ['src/sgd/convert/data/strains/orf_genomic_1000_all.fasta',
                        'src/sgd/convert/data/strains/rna_genomic_1000.fasta']

    # >YAL001C TFC3 SGDID:S000000001, Chr I from 152166-146594, Genome Release 64-2-1, reverse complement, Verified ORF, "Subunit of RNA polymerase III transcription initiation factor complex; part of the TauB domain of TFIIIC that binds DNA at the BoxB promoter sites of tRNA and similar genes; cooperates with Tfc6p in DNA binding; largest of six subunits of the RNA polymerase III transcription initiation factor complex (TFIIIC)"
 
    # >HRA1 HRA1 SGDID:S000119380, Chr I from 98305-100868, Genome Release 64-2-1, ncRNA_gene, "Non-protein-coding RNA; substrate of RNase P, possibly involved in rRNA processing, specifically maturation of 20S precursor into the mature 18S rRNA"


    # for seqfile in genomic_1k_files:
    #    f = open(seqfile, 'r')
    #    for name, (file_header, residues) in get_sequence_library_fsa(f).iteritems():
    #        if name == 'tS(GCU)L':
    #            name = 'tX(XXX)L'
    #        elif name == 'tT(XXX)Q2':
    #            name = 'tT(UAG)Q2'
    #        dbentity_id = locus_to_dbentity_id.get(name)
    #        if dbentity_id is None:
    #            print "The feature ", name, " is not in DBENTITY table."
    #            continue
    #
    #        download_filename = name + '-1kb.fsa'
    #        Chr I from 152166-146594, Genome Release
    #        coords = file_header.replace(', Genome Release 64-2-1', '').split('from ')[1].split('-')
    #        start_index = coords[0]
    #        end_index = coords[1]
    #        if start_index > end_index:
    #            start_index, end_index = end_index, start_index 
    #         
            # yield { 'source': { "display_name": 'SGD'},
            #        'taxonomy_id': taxonomy_id,
            #        'dbentity_id': name_to_dbentity_id[name],
            #        'dna_type': '1KB',
            #        'so_id': name_to_so_id[name],
            #        'residues': residues,
            #        'seq_version': name_to_seq_version[name],
            #        'coord_version': name_to_coord_version[name],
            #        'contig_id': name_to_contig_id[name]
            #        'start_index': start_index,
            #        'end_index': end_index,
            #        'strand': name_to_strand[name],
            #        'file_header': file_header,
            #        'download_filename': download_filename,
            #        'date_created': name_to_date_created[name],
            #        'created_by': name_to_created_by[name] }
    #    f.close()
    
    
    nex_session.close()
    bud_session.close()
    

def get_feature_type_list():

    return [ "ARS", 
             "LTR_retrotransposon", 
             "ORF", 
             "blocked_reading_frame", 
             "disabled_reading_frame", 
             "centromere", 
             "gene_group", 
             "long_terminal_repeat",
             "mating_type_region",
             "matrix_attachment_site", 
             "ncRNA_gene",
             "origin_of_replication",
             "pseudogene",
             "rRNA_gene",
             "silent_mating_type_cassette_array",
             "snRNA_gene", 
             "snoRNA_gene", 
             "tRNA_gene",
             "telomerase_RNA_gene",
             "telomere",
             "transposable_element_gene" ]

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dnasequenceannotation_starter, 'dnasequen\
ceannotation', lambda x: (x['dbentity_id'], x['taxonomy_id'], x['so_id'], x['dna_type'], x['contig_id']))
