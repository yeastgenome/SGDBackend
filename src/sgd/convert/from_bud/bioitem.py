from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import joinedload

from src.sgd.convert import create_format_name, number_to_roman
from src.sgd.convert.transformers import make_db_starter, \
    make_file_starter, make_fasta_file_starter
import os
from decimal import Decimal

__author__ = 'kpaskov'



# --------------------- Convert Contig ---------------------
def update_contig_centromeres(nex_session_maker):
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    from src.sgd.model.nex.bioitem import Contig
    from src.sgd.model.nex.bioentity import Locus

    nex_session = nex_session_maker()

    centromere_ids = [x.id for x in nex_session.query(Locus).filter_by(locus_type='centromere').all()]
    contig_id_to_start_end = dict()
    for dnasequenceevidence in nex_session.query(DNAsequenceevidence).filter(DNAsequenceevidence.locus_id.in_(centromere_ids)).all():
        contig_id_to_start_end[dnasequenceevidence.contig_id] = (dnasequenceevidence.start, dnasequenceevidence.end)

    for contig in nex_session.query(Contig).filter(Contig.id.in_(contig_id_to_start_end.keys())).all():
        centromere_start, centromere_end = contig_id_to_start_end[contig.id]
        contig.centromere_start = centromere_start
        contig.centromere_end = centromere_end
        print contig.id

    nex_session.commit()
    nex_session.close()

def update_contig_reference_alignment(nex_session_maker):
    from src.sgd.model.nex.bioitem import Contig

    nex_session = nex_session_maker()
    genbank_id_to_contig = dict([(x.genbank_accession, x) for x in nex_session.query(Contig).all() if x.genbank_accession is not None])
    refseq_id_to_contig = dict([(x.refseq_id, x) for x in genbank_id_to_contig.values()])

    contig_id_to_reference_alignment = dict()
    f = open('src/sgd/convert/data/blast_hits.txt', 'r')
    state = 'start'
    for line in f:
        if line.startswith('#'):
            state = '#'
        elif state == '#':
            state = 'data'
            pieces = line.split()
            first_column = pieces[0].split('|')
            contig_genbank_id = first_column[3]
            second_column = pieces[1].split('|')
            reference_chromosome_refseq_id = second_column[3]
            percent_identity = Decimal(pieces[2])
            alignment_length = int(pieces[3])
            start = int(pieces[8])
            end = int(pieces[9])
            reference_chromosome_id = refseq_id_to_contig[reference_chromosome_refseq_id].id
            contig_id_to_reference_alignment[genbank_id_to_contig[contig_genbank_id].id] = [reference_chromosome_id, start, end, percent_identity, alignment_length]

    for contig in genbank_id_to_contig.values():
        if contig.id in contig_id_to_reference_alignment:
            reference_alignment = contig_id_to_reference_alignment[contig.id]
            contig.reference_chromosome_id = reference_alignment[0]
            contig.reference_start = reference_alignment[1]
            contig.reference_end = reference_alignment[2]
            contig.reference_percent_identity = reference_alignment[3]
            contig.reference_alignment_length = reference_alignment[4]

    nex_session.commit()
    nex_session.close()

strains_with_chromosomes = set(['S288C'])
def make_contig_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioitem import Contig
    from src.sgd.convert.from_bud import sequence_files, new_sequence_files
    from src.sgd.model.bud.feature import Feature


    def contig_starter():
        nex_session = nex_session_maker()
        bud_session = bud_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        for sequence_filename, coding_sequence_filename, strain in sequence_files:
            filenames = []
            if isinstance(sequence_filename, list):
                filenames = sequence_filename
            elif sequence_filename is not None:
                filenames.append(sequence_filename)
            for filename in filenames:
                for sequence_id, residues in make_fasta_file_starter(filename)():
                    gi_number = sequence_id.split('|')[1]
                    genbank_accession = sequence_id.split('|')[3]
                    yield {'source': key_to_source['SGD'],
                           'strain': key_to_strain[strain.replace('.', '')],
                           'residues': residues,
                           'is_chromosome': strain in strains_with_chromosomes,
                           'genbank_accession': genbank_accession,
                           'gi_number': gi_number}

        for sequence_filename, coding_sequence_filename, strain in new_sequence_files:
            filenames = []
            if isinstance(sequence_filename, list):
                filenames = sequence_filename
            elif sequence_filename is not None:
                filenames.append(sequence_filename)
            for filename in filenames:
                for sequence_id, residues in make_fasta_file_starter(filename)():
                    name = sequence_id.split(' ')[0]
                    gi_number = name.split('|')[1]
                    genbank_accession = name.split('|')[3]
                    if genbank_accession != '.':
                        yield {'source': key_to_source['SGD'],
                               'strain': key_to_strain[strain.replace('.', '')],
                               'residues': residues,
                               'is_chromosome': strain in strains_with_chromosomes,
                               'genbank_accession': genbank_accession,
                               'gi_number': gi_number}

        s288c_chromosome_to_genbank__refseq_id = {'Chromosome I': ('BK006935.2', 'NC_001133.9'),
                                          'Chromosome II': ('BK006936.2', 'NC_001134.8'),
                                          'Chromosome III': ('BK006937.2', 'NC_001135.5'),
                                          'Chromosome IV': ('BK006938.2', 'NC_001136.10'),
                                          'Chromosome V': ('BK006939.2', 'NC_001137.3'),
                                          'Chromosome VI': ('BK006940.2', 'NC_001138.5'),
                                          'Chromosome VII': ('BK006941.2', 'NC_001139.9'),
                                          'Chromosome VIII': ('BK006934.2', 'NC_001140.6'),
                                          'Chromosome IX': ('BK006942.2', 'NC_001141.2'),
                                          'Chromosome X': ('BK006943.2', 'NC_001142.9'),
                                          'Chromosome XI': ('BK006944.2', 'NC_001143.9'),
                                          'Chromosome XII': ('BK006945.2', 'NC_001144.5'),
                                          'Chromosome XIII': ('BK006946.2', 'NC_001145.3'),
                                          'Chromosome XIV': ('BK006947.3', 'NC_001146.8'),
                                          'Chromosome XV': ('BK006948.2', 'NC_001147.6'),
                                          'Chromosome XVI': ('BK006949.2', 'NC_001148.4'),
                                          'Chromosome Mito': ('AJ011856.1', 'NC_001224.1')}


        #S288C Contigs
        from src.sgd.model.bud.sequence import Sequence
        for feature in bud_session.query(Feature).filter(or_(Feature.type == 'chromosome', Feature.type == 'plasmid')).all():
            for sequence in feature.sequences:
                if sequence.is_current == 'Y':
                    display_name = 'Chromosome ' + (feature.name if feature.name not in number_to_roman else number_to_roman[feature.name])
                    genbank_accession = None
                    refseq_id = None
                    if display_name in s288c_chromosome_to_genbank__refseq_id:
                        genbank_accession, refseq_id = s288c_chromosome_to_genbank__refseq_id[display_name]
                    yield {'display_name': display_name,
                           'format_name': display_name.replace(' ', '_'),
                           'source': key_to_source['SGD'],
                           'strain': key_to_strain['S288C'],
                           'residues': sequence.residues,
                           'is_chromosome': 1,
                           'genbank_accession': genbank_accession,
                           'refseq_id': refseq_id}

        nex_session.close()
        bud_session.close()
    return contig_starter

# --------------------- Convert Reservedname ---------------------
def make_reservedname_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.feature import GeneReservation
    from src.sgd.model.bud.reference import Reflink

    def reservedname_starter():
        nex_session = nex_session_maker()
        bud_session = bud_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])

        locus_id_to_reference = dict([(x.primary_key, x.reference_id) for x in bud_session.query(Reflink).filter_by(tab_name='GENE_RESERVATION')])

        for gene_reservation in bud_session.query(GeneReservation).filter_by(date_standardized=None).all():
            yield {
                'display_name': gene_reservation.reserved_gene_name,
                'locus': None if gene_reservation.id not in id_to_bioentity else id_to_bioentity[gene_reservation.id],
                'reference': None if gene_reservation.id not in locus_id_to_reference else id_to_reference[locus_id_to_reference[gene_reservation.id]],
                'reservation_date': gene_reservation.reservation_date,
                'expiration_date': gene_reservation.expiration_date,
                'source': key_to_source['SGD'],
                'date_created': gene_reservation.date_created,
                'created_by': gene_reservation.created_by
            }

        nex_session.close()
        bud_session.close()
    return reservedname_starter

# --------------------- Convert Pathway ---------------------
def make_pathway_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.general import Dbxref

    def pathway_starter():
        nex_session = nex_session_maker()
        bud_session = bud_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for dbxref in bud_session.query(Dbxref).filter_by(dbxref_type='Pathway ID').all():
            yield {
                'format_name': dbxref.dbxref_id,
                'display_name': dbxref.dbxref_name,
                'source': key_to_source[dbxref.source],
                'link': 'http://pathway.yeastgenome.org/YEAST/new-image?type=PATHWAY&object=' + dbxref.dbxref_id + '&detail-level=2',
                'date_created': dbxref.date_created,
                'created_by': dbxref.created_by
            }

        nex_session.close()
        bud_session.close()
    return pathway_starter

# --------------------- Convert Dataset ---------------------
def make_dataset_starter(nex_session_maker, expression_dir):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    def dataset_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])

        filename_to_channel_count = dict([(x[0], x[1].strip()) for x in make_file_starter(expression_dir + '/channel_count.txt')()])

        for path in os.listdir(expression_dir):
            if os.path.isdir(expression_dir + '/' + path):
                full_description = None
                geo_id = None
                pcl_filename_to_info = {}
                pubmed_id = None

                state = 'BEGIN'
                try:
                    for row in make_file_starter(expression_dir + '/' + path + '/README')():
                        if row[0].startswith('Full Description'):
                            state = 'FULL_DESCRIPTION:'
                            full_description = row[0][18:].strip()
                        elif row[0].startswith('PMID:'):
                            pubmed_id = int(row[0][6:].strip())
                        elif row[0].startswith('GEO ID:'):
                            geo_id = row[0][8:].strip().split('.')[0].split('GPL')[0]
                        elif row[0].startswith('PCL filename'):
                            state = 'OTHER'
                        elif state == 'FULL_DESCRIPTION':
                            full_description = full_description + row[0].strip()
                        elif state == 'OTHER':
                            pcl_filename = row[0].strip()
                            short_description = row[1].strip()
                            tag = row[3].strip()
                            pcl_filename_to_info[pcl_filename] = (short_description, tag)

                    if geo_id == 'N/A':
                        geo_id = None

                    for file in os.listdir(expression_dir + '/' + path):
                        if file != 'README':
                            f = open(expression_dir + '/' + path + '/' + file, 'r')
                            pieces = f.next().split('\t')
                            f.close()

                            if pubmed_id not in pubmed_id_to_reference:
                                print 'Warning: pubmed_id not found ' + str(pubmed_id)

                            if file in pcl_filename_to_info:
                                yield {
                                    'description': full_description,
                                    'geo_id': geo_id,
                                    'pcl_filename': file,
                                    'short_description': pcl_filename_to_info[file][0],
                                    'tags': pcl_filename_to_info[file][1],
                                    'reference': None if pubmed_id is None or pubmed_id not in pubmed_id_to_reference else pubmed_id_to_reference[pubmed_id],
                                    'source': key_to_source['SGD'],
                                    'channel_count': 1 if file not in filename_to_channel_count else int(filename_to_channel_count[file]),
                                    'condition_count': len(pieces)-3
                                }
                            else:
                                print 'Filename not in readme: ' + file
                except:
                    print 'File ' + expression_dir + '/' + path + '/README' + ' not found.'

        nex_session.close()
    return dataset_starter

# --------------------- Convert Dataset Column---------------------
def make_datasetcolumn_starter(nex_session_maker, expression_dir):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Dataset
    def datasetcolumn_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_dataset = dict([(x.unique_key(), x) for x in nex_session.query(Dataset).all()])


        key_to_GSM = dict([((x[0], x[1].strip().decode('ascii','ignore')), x[2]) for x in make_file_starter('src/sgd/convert/data/microarray_05_14/GSM_to_GSE.txt')()])

        for path in os.listdir(expression_dir):
            if os.path.isdir(expression_dir + '/' + path):
                for file in os.listdir(expression_dir + '/' + path):
                    dataset_key = (file[:-4], 'DATASET')
                    if dataset_key in key_to_dataset:
                        f = open(expression_dir + '/' + path + '/' + file, 'r')
                        pieces = f.next().split('\t')
                        f.close()

                        geo_id = key_to_dataset[dataset_key].geo_id



                        i = 0
                        for piece in pieces[3:]:
                            column_name = piece.strip().decode('ascii','ignore')

                            if (geo_id, column_name) not in key_to_GSM and geo_id is not None:
                                print (geo_id, column_name)
                            #print (geo_id, column_name)
                            col_geo_id = None if (geo_id, column_name) not in key_to_GSM else key_to_GSM[(geo_id, column_name)]
                            link = None if col_geo_id is None else 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + col_geo_id
                            yield {
                                        'description': column_name,
                                        'dataset': key_to_dataset[dataset_key],
                                        'source': key_to_source['SGD'],
                                        'file_order': i,
                                        'geo_id': col_geo_id,
                                        'link': link
                            }
                            i += 1

        nex_session.close()
    return datasetcolumn_starter


# --------------------- Convert Bioitem URL ---------------------
def make_bioitem_url_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Domain, Chemical, Dataset, Contig

    def bioitem_url_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])



        for dataset in nex_session.query(Dataset).all():
            if dataset.geo_id is not None:
                yield {'display_name': dataset.geo_id,
                       'link': 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + dataset.geo_id,
                       'source': key_to_source['NCBI'],
                       'category': 'External',
                       'bioitem_id': dataset.id}

        pcl_filename_to_dataset = dict([(x.pcl_filename, x) for x in nex_session.query(Dataset).all()])

        for path in os.listdir('src/sgd/convert/data/microarray_05_14'):
            if os.path.isdir('src/sgd/convert/data/microarray_05_14/' + path):
                for file in os.listdir('src/sgd/convert/data/microarray_05_14/' + path):
                    if file != 'README':
                        if file in pcl_filename_to_dataset:
                            dataset = pcl_filename_to_dataset[file]
                            yield {'display_name': 'Download Data',
                                   'link': 'http://downloads.yeastgenome.org/expression/microarray/' + path + '/',
                                   'source': key_to_source['SGD'],
                                   'category': 'Download',
                                   'bioitem_id': dataset.id}

        for contig in nex_session.query(Contig).all():
            if contig.genbank_accession is not None:
                yield {'display_name': contig.genbank_accession,
                             'link': 'http://www.ncbi.nlm.nih.gov/nuccore/' + contig.genbank_accession,
                             'source': key_to_source['GenBank-EMBL-DDBJ'],
                             'category': 'External',
                             'bioitem_id': contig.id}

        nex_session.close()
    return bioitem_url_starter

# --------------------- Convert Bioitem Tag ---------------------
def make_bioitem_tag_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Tag
    from src.sgd.model.nex.bioitem import Dataset
    def bioitem_tag_starter():
        nex_session = nex_session_maker()

        key_to_dataset = dict([(x.unique_key(), x) for x in nex_session.query(Dataset).all()])
        key_to_tag = dict([(x.unique_key(), x) for x in nex_session.query(Tag).all()])

        for row in make_file_starter('src/sgd/convert/data/microarray_05_14/SPELL-tags.txt')():
            dataset_key = (row[1].strip()[:-4], 'DATASET')
            tags = row[2].strip()
            for t in [x.strip() for x in tags.split('|')]:
                if t != '':
                    yield {
                        'bioitem': key_to_dataset[dataset_key],
                        'tag': key_to_tag[create_format_name(t)]
                    }

        nex_session.close()
    return bioitem_tag_starter


