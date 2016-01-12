from src.sgd.convert import basic_convert
from src.sgd.convert.sequence_files import sequence_files, new_sequence_files
from src.sgd.convert.util import make_fasta_file_starter, number_to_roman, \
    get_dna_sequence_library, get_sequence, get_ref_sequence_library_fsa, \
    get_sequence_with_contig_library_fsa, reverse_complement, \
    get_strain_taxid_mapping

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

    strain_to_strain_id =  dict([(x.format_name, x.id) for x in nex_session.query(Strain).all()])
    contig_name_to_contig = dict([(x.format_name, x) for x in nex_session.query(Contig).all()])    
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    genomerelease_to_genomerelease_id =  dict([(x.display_name, x.id) for x in nex_session.query(Genomerelease).all()])
    bud_id_to_genomerelease_id =  dict([(x.bud_id, x.id) for x in nex_session.query(Genomerelease).all()])
    type_to_so_id = dict([(x.display_name, x.id) for x in nex_session.query(So).all()]) 
    locus_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    strain_to_taxid_mapping = get_strain_taxid_mapping()
    
    ########### load the sequences from old strains
    for sequence_filename, coding_sequence_filename, strain in sequence_files:
        strain_id = strain_to_strain_id.get(strain.replace('.', ''))
        if strain_id is None:
            print "The strain ", strain, " is not in STRAIN table."
            continue
        taxid = strain_to_taxid_mapping.get(strain)
        if taxid is None:
            print "The strain: ", strain, " is not mapped to a TAXON ID."
            continue

        taxonomy_id = taxid_to_taxonomy_id.get(taxid)
        if taxonomy_id is None:
            print "The strain ", strain, " is not in TAXONOMY table."
            continue

        ### load genomic sequences and genomic sequences with 1kb from old strains

        name_to_coords = {}
        name_to_record = {}

        sequence_filenames = []
        if isinstance(sequence_filename, list):
            sequence_filenames = sequence_filename
        elif sequence_filename is not None:
            sequence_filenames.append(sequence_filename)

        for seq_file in sequence_filenames:

            f = open(seq_file, 'r')
            sequence_library = get_dna_sequence_library(f)
            f.close()

            f = open(seq_file, 'r')
            for row in f:
                pieces = row.split('\t')
                if len(pieces) == 9 and pieces[2] != 'contig':
                    parent_id = pieces[0]
                    start = int(pieces[3])
                    end = int(pieces[4])
                    strand = pieces[6]
                    info = get_info(pieces[8])
                    class_type = pieces[2]
                    residues = get_sequence(parent_id, start, end, strand, sequence_library)
                    if 'Name' in info and 'Parent' not in info:
                        name = info['Name'].strip().replace('%28', "(").replace('%29', ")")
                        if name.endswith('_mRNA'):
                            name = name[:-5]
                        elif name == 'tS(GCU)L':
                            name = 'tX(XXX)L'
                        elif name == 'tT(XXX)Q2':
                            name = 'tT(UAG)Q2'
                        elif name == '15S_rRNA':
                            name = 'Q0020'
                        elif name == '21S_rRNA':
                            name = 'Q0158'
                        gene = name
                        if 'gene' in info:
                            gene = info['gene']
                        
                        dbentity_id = locus_to_dbentity_id.get(name)
                        if dbentity_id is None:
                            print "The locus: ", name, " is not in DBENTITY table."
                            continue        
                                                                    
                        contig = parent_id.split('|')[3]
                        if contig == '.':
                            continue
                        contig_obj = contig_name_to_contig.get(contig)
                        if contig_obj is None:
                            print "The contig: ", contig, " is not in CONTIG table. The parent_id=", parent_id
                            continue
                        if class_type == 'gene':
                            class_type = 'ORF'
                        elif class_type.endswith('RNA'):
                            class_type = class_type + "_gene"
                        so_id = type_to_so_id.get(class_type)
                        if so_id is None:
                            print "The feature type: ", class_type, " is not in SO table."
                            continue

                        ### genomic sequences

                        genomic_data = load_strain_genomic(name, gene, strain, contig_obj, 
                                                           start, end, strand, residues, 
                                                           taxonomy_id, dbentity_id, 
                                                           so_id, name_to_record)
                        yield genomic_data

                        ### genomic 1KB sequence
                        genomic_1kb_data = load_strain_genomic_1kb(name, gene, strain, taxonomy_id, 
                                                                   dbentity_id, so_id, start, 
                                                                   end, strand, contig_obj)
                        yield genomic_1kb_data

                    elif class_type == 'CDS':
                        name = info['Name'].replace('_CDS', '')
                        if name in name_to_coords:
                            name_to_coords[name] = name_to_coords[name] + ',' + str(start)+'..'+str(end)
                        else:
                            name_to_coords[name] = str(start)+'..'+str(end)
            f.close()


        ### load coding sequences for old strains
        # coding_data = load_strain_coding_sequence(strain, taxonomy_id, residues, 
        #                                          coding_sequence_filename, 
        #                                          name_to_record, name_to_coords)
        # for data in coding_data:
        #    yield data


    strain_to_strain_type =  dict([(x.format_name, x.strain_type) for x in nex_session.query(Strain).all()])

    ########### load sequences for the 25 new stanford strains
    
    for sequence_filename, coding_sequence_filename, strain in new_sequence_files:
        strain = strain.replace('.', '')
        strain_id = strain_to_strain_id.get(strain)
        if strain_id is None:
            print "The strain ", strain, " is not in STRAIN table."
            continue
        taxid = strain_to_taxid_mapping.get(strain)
        if taxid is None:
            print "The strain: ", strain, " is not mapped to a TAXON ID."
            continue

        taxonomy_id = taxid_to_taxonomy_id.get(taxid)
        if taxonomy_id is None:
            print "The strain ", strain, " is not in TAXONOMY table."
            continue

        ### load genomic sequences and genomic sequences with 1kb from the new strains

        f = open(sequence_filename, 'r')
        sequence_library = get_dna_sequence_library(f, remove_spaces=True)
        f.close()

        name_to_coords = {}
        name_to_record = {}

        f = open(sequence_filename, 'r')
        for row in f:
            pieces = row.split(' ')
            if len(pieces) >= 9 and pieces[2] != 'contig' and not row.startswith('>'):
                parent_id = pieces[0]
                start = int(pieces[3])
                end = int(pieces[4])
                strand = pieces[6]
                infos = pieces[8].split(',')
                residues = get_sequence(parent_id, start, end, strand, sequence_library)
                class_type = pieces[2]

                if class_type != 'CDS' and class_type != 'intron':
                    for info in infos:
                        name = infos[0].strip()
                        if name == '15S_rRNA':
                            name = 'Q0020'
                        elif name == '21S_rRNA':
                            name = 'Q0158'
                        gene = name
                        if len(infos) > 5:
                            gene = infos[5].strip()
                        
                        dbentity_id = locus_to_dbentity_id.get(name)
                        if dbentity_id is None:
                            print "The locus: ", name, " is not in DBENTITY table."
                            continue                                                                
 
                        contig = parent_id.split('|')[3]
                        if contig == '.':
                            continue
                        contig_obj = contig_name_to_contig.get(contig)
                        if contig_obj is None:
                            print "The contig: ", contig, " is not in CONTIG table. The parent_id=", parent_id
                            continue
                        if class_type == 'gene':
                            class_type = 'ORF'
                        elif class_type.endswith('RNA'):
                            class_type = class_type + "_gene"
                        so_id = type_to_so_id.get(class_type)
                        if so_id is None:
                            print "The feature type: ", class_type, " is not in SO table."
                            continue

                        ### genomic sequences

                        genomic_data = load_strain_genomic(name, gene, strain, contig_obj, 
                                                           start, end, strand, residues,
                                                           taxonomy_id, dbentity_id, 
                                                           so_id, name_to_record)
                        yield genomic_data

                        ### genomic 1KB sequence

                        genomic_1kb_data = load_strain_genomic_1kb(name, gene, strain, taxonomy_id, 
                                                                   dbentity_id, so_id, start, 
                                                                   end, strand, contig_obj)
                        yield genomic_1kb_data

                elif class_type == 'CDS':
                    name = infos[0].strip()
                    if name in name_to_coords:
                        name_to_coords[name] = name_to_coords[name] + ',' + str(start)+'..'+str(end)
                    else:
                        name_to_coords[name] = str(start)+'..'+str(end)

        f.close()

        if strain_to_strain_type.get(strain) == 'Other':
            continue
                    
        #### load coding sequences from the 11 alternative strains only
        coding_data = load_strain_coding_sequence(strain, taxonomy_id, residues, 
                                                  coding_sequence_filename, 
                                                  name_to_record, name_to_coords,
                                                  contig_name_to_contig)
        for data in coding_data: 
            yield data

    ########### load genomic sequences for S288C  

    from sqlalchemy.sql.expression import or_
    from src.sgd.model.bud.feature import Feature, FeatRel
    from src.sgd.model.bud.sequence import Sequence, Feat_Location, FeatLocation_Rel

    feature_types = get_feature_type_list()

    taxid = strain_to_taxid_mapping['S288C']
    taxonomy_id = taxid_to_taxonomy_id[taxid]

    bud_id_to_contig_id = dict()
    bud_id_to_chr = dict()

    print "Getting data from BUD..."

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    child_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in bud_session.query(FeatRel).filter_by(rank=1).all()]) 
    id_to_feature = dict([(x.id, x) for x in bud_session.query(Feature).all()])
    feature_location_id_to_release_bud_id = dict([(x.feature_location_id, x.release_id) for x in bud_session.query(FeatLocation_Rel).all()])
    
    for bud_id in child_id_to_parent_id: 
        chr_id = child_id_to_parent_id[bud_id]
        if id_to_feature[chr_id].name in number_to_roman:
            chr_name = 'Chromosome_' + number_to_roman[id_to_feature[chr_id].name] 
            bud_id_to_chr[bud_id] = number_to_roman[id_to_feature[chr_id].name]
        else:
            chr_name = 'Chromosome_' + id_to_feature[bud_id].name
            bud_id_to_chr[bud_id] = id_to_feature[bud_id].name
        if chr_name in contig_name_to_contig:
            bud_id_to_contig_id[bud_id] = contig_name_to_contig[chr_name].id

    name_to_this_record = {}

    plasmid_x = nex_session.query(Contig).filter_by(format_name="2-micron_plasmid").first()   
    plasmid_contig_id = plasmid_x.id
    
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
            so_id = type_to_so_id.get(type)
            if name.startswith('R00'):
                contig_id = plasmid_contig_id
                so_id = type_to_so_id.get('ORF')
            if contig_id is None:
                print "The feature ", name, " is not mapped to a chromosome."
                continue
            if so_id is None:
                print "The feature_type ", type, " is not in SO table."
                continue

            release_bud_id = feature_location_id_to_release_bud_id.get(bud_location.id)
            release_id = bud_id_to_genomerelease_id.get(release_bud_id)

            name_to_this_record[name] = { "dbentity_id": dbentity_id,
                                          "contig_id": contig_id,
                                          "so_id": so_id,
                                          "start": bud_location.min_coord,
                                          "end": bud_location.max_coord,
                                          "strand": bud_location.strand,
                                          "seq_version": str(bud_location.sequence.seq_version),
                                          "coord_version": str(bud_location.coord_version),
                                          "date_created": str(bud_location.sequence.date_created),
                                          "created_by": str(bud_location.sequence.created_by),
                                          "release_id": release_id }

            if gene_name is None:
                gene_name = name
            file_header = ">" + name + " " + gene_name + " SGDID:" + sgdid + " chr" + chr + ":"
            if bud_location.strand == '-':
                file_header = file_header + str(bud_location.max_coord) + ".." + str(bud_location.min_coord)
            else:
                file_header = file_header + str(bud_location.min_coord) + ".." + str(bud_location.max_coord)
            file_header = file_header + " [Genome Release 64-2-1]"
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
                    'genomerelease_id': release_id,
                    'download_filename': download_filename,
                    'date_created': str(bud_location.sequence.date_created),
                    'created_by': bud_location.sequence.created_by }

    ## load coding sequences for S288C

    coding_sequence_files = [ 'src/sgd/convert/data/strains/orf_coding_all.fasta',
                              'src/sgd/convert/data/strains/rna_coding.fasta']

    for seqfile in coding_sequence_files:
        f = open(seqfile, 'r')
        for name, (file_header, residues) in get_ref_sequence_library_fsa(f).iteritems():
            if name == 'tS(GCU)L':
                name = 'tX(XXX)L'
            elif name == 'tT(XXX)Q2':
                name = 'tT(UAG)Q2'
            download_filename = name + '-coding.fsa'
            dbentity_id = locus_to_dbentity_id.get(name)
            if dbentity_id is None:
                print "The feature ", name, " is not in DBENTITY table."
                continue

            record = name_to_this_record[name]
            if name.startswith('R00'):
                record["so_id"] = type_to_so_id['ORF']

            if len(residues) < record["end"] - record["start"] + 1:
                ## there is intron
                file_header = file_header.replace(" [Genome Release 64-2-1]", " intron sequence removed [Genome Release 64-2-1]")

            yield { 'source': { "display_name": 'SGD'},
                    'taxonomy_id': taxonomy_id,
                    'dbentity_id': dbentity_id,
                    'dna_type': 'CODING',
                    'so_id': record["so_id"],
                    'residues': residues,
                    'seq_version': record["seq_version"],
                    'coord_version': record["coord_version"],
                    'contig_id': record["contig_id"],
                    'start_index': record["start"],
                    'end_index': record["end"],
                    'strand': record["strand"],
                    'file_header': file_header,
                    'download_filename': download_filename,
                    'genomerelease_id': record["release_id"],
                    'date_created': record["date_created"],
                    'created_by': record["created_by"] } 

        f.close()

    ### load genomic_1k sequences for S288C

    genomic_1k_files = ['src/sgd/convert/data/strains/orf_genomic_1000_all.fasta',
                        'src/sgd/convert/data/strains/rna_genomic_1000.fasta']

    for seqfile in genomic_1k_files:
        f = open(seqfile, 'r')
        for name, (file_header, residues) in get_ref_sequence_library_fsa(f).iteritems():
            if name == 'tS(GCU)L':
                name = 'tX(XXX)L'
            elif name == 'tT(XXX)Q2':
                name = 'tT(UAG)Q2'
            dbentity_id = locus_to_dbentity_id.get(name)
            if dbentity_id is None:
                print "The feature ", name, " is not in DBENTITY table."
                continue
    
            record = name_to_this_record[name]

            download_filename = name + '-1kb.fsa'
            coords = file_header.replace(' [Genome Release 64-2-1]', '').split(':')[2].split('..')
            start_index = int(coords[0])
            end_index = int(coords[1])
            file_header = file_header.replace(" [Genome Release 64-2-1]", " +/- 1kb [Genome Release 64-2-1]")
            if start_index > end_index:
                start_index, end_index = end_index, start_index 
             
            yield { 'source': { "display_name": 'SGD'},
                    'taxonomy_id': taxonomy_id,
                    'dbentity_id': dbentity_id,
                    'dna_type': '1KB',
                    'so_id': record["so_id"],
                    'residues': residues,
                    'seq_version': record["seq_version"],
                    'coord_version': record["coord_version"],
                    'contig_id': record["contig_id"],
                    'start_index': start_index,
                    'end_index': end_index,
                    'strand': record["strand"],
                    'file_header': file_header,
                    'download_filename': download_filename,
                    'genomerelease_id': record["release_id"],
                    'date_created': record["date_created"],
                    'created_by': record["created_by"] }
        f.close()
    
    nex_session.close()
    bud_session.close()

def load_strain_genomic_1kb(name, gene, strain, taxonomy_id, dbentity_id, so_id, start, end, strand, contig_obj):

    start_1kb = max(1, start - 1000)
    end_1kb = min(len(contig_obj.residues), end + 1000)
    residues_1kb = contig_obj.residues[start_1kb - 1:end_1kb]
    if strand == '-':
        residues_1kb = reverse_complement(residues_1kb)
    file_header_1kb = ">" + name + " " + gene + " " + strain + " " + contig_obj.display_name + ":" + str(start_1kb) + ".." + str(end_1kb) + " +/- 1kb"
    download_filename_1kb = name + "_" + strain + "_1kb.fsa"
    return { 'source': { "display_name": 'SGD'},
             'taxonomy_id': taxonomy_id,
             'dbentity_id': dbentity_id,
             'dna_type': '1KB',
             'so_id': so_id,
             'residues': residues_1kb,
             'contig_id': contig_obj.id,
             'start_index': start_1kb,
             'end_index': end_1kb,
             'strand': strand,
             'file_header': file_header_1kb,
             'download_filename': download_filename_1kb }

def load_strain_genomic(name, gene, strain, contig_obj, start, end, strand, residues, taxonomy_id, dbentity_id, so_id, name_to_record):

    file_header = ">" + name + " " + gene + " " + strain + " " + contig_obj.display_name + ":" + str(start) + ".." + str(end)
    download_filename = name + "_" + strain + "_genomic.fsa"

    name_to_record[name] = { "dbentity_id": dbentity_id,
                             "so_id": so_id,
                             "contig": contig_obj.display_name,
                             "contig_id": contig_obj.id,
                             "start": start,
                             "end": end,
                             "strand": strand,
                             "gene": gene }

    return {'source': { "display_name": 'SGD'},
            'taxonomy_id': taxonomy_id,
            'dbentity_id': dbentity_id,
            'dna_type': 'GENOMIC',
            'so_id': so_id,
            'residues': residues,
            'contig_id': contig_obj.id,
            'start_index': start,
            'end_index': end,
            'strand': strand,
            'file_header': file_header,
            'download_filename': download_filename }

def load_strain_coding_sequence(strain, taxonomy_id, residues, coding_sequence_filename, name_to_record, name_to_coords, contig_name_to_contig):

    coding_sequence_filenames = []
    if isinstance(coding_sequence_filename, list):
        coding_sequence_filenames = coding_sequence_filename
    elif coding_sequence_filename is not None:
        coding_sequence_filenames.append(coding_sequence_filename)

    data = []
    for coding_seq_file in coding_sequence_filenames:
        f = open(coding_seq_file, 'r')
        for (name, contig_name), residues in get_sequence_with_contig_library_fsa(f).iteritems():

            if name == 'tS(GCU)L':
                name = 'tX(XXX)L'
            elif name == 'tT(XXX)Q2':
                name = 'tT(UAG)Q2'
            if name == 'UNDEF':
                continue

            record = name_to_record.get(name)
            if record is None:
                continue
            
            if contig_name is None:
                print "No contig name for strain: ", strain
                continue
            contig_obj = contig_name_to_contig.get(contig_name)
            if contig_obj is None:
                print "The contig: ", contig_name, " is not in the CONTIG Table."
                continue
            contig_id = contig_obj.id

            file_header = ">" + name + " " + record["gene"] + " " + strain + " " + contig_name + ":"
            if name in name_to_coords:
                file_header = file_header + name_to_coords[name]
            else:
                file_header = file_header + str(record["start"]) + ".." + str(record["end"])

            if name in name_to_coords and "," in name_to_coords[name]:
                file_header = file_header + " intron sequence removed"
            download_filename = name + "_" + strain + "_coding.fsa"
        
            data.append( { 'source': { "display_name": 'SGD'},
                           'taxonomy_id': taxonomy_id,
                           'dbentity_id': record["dbentity_id"],
                           'dna_type': 'CODING',
                           'so_id': record["so_id"],
                           'residues': residues,
                           'contig_id': contig_id,
                           'start_index': record["start"],
                           'end_index': record["end"],
                           'strand': record["strand"],
                           'file_header': file_header,
                           'download_filename': download_filename } )
        f.close()

        return data


def get_info(data):
    info = {}
    for entry in data.split(';'):
        pieces = entry.split('=')
        if len(pieces) == 2:
            info[pieces[0]] = pieces[1]
    return info

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
