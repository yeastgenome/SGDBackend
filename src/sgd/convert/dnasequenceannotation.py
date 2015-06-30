from decimal import Decimal
from src.sgd.convert.into_curate import basic_convert
from src.sgd.convert.into_curate.locus import non_locus_feature_types
from sqlalchemy.orm import joinedload

__author__ = 'kpaskov'


strains_with_chromosomes = set(['S288C'])

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

number_to_roman = {'01': 'I', '1': 'I',
                   '02': 'II', '2': 'II',
                   '03': 'III', '3': 'III',
                   '04': 'IV', '4': 'IV',
                   '05': 'V', '5': 'V',
                   '06': 'VI', '6': 'VI',
                   '07': 'VII', '7': 'VII',
                   '08': 'VIII', '8': 'VIII',
                   '09': 'IX', '9': 'IX',
                   '10': 'X',
                   '11': 'XI',
                   '12': 'XII',
                   '13': 'XIII',
                   '14': 'XIV',
                   '15': 'XV',
                   '16': 'XVI',
                   '17': 'Mito',
                   }


def load_contig_urls(obj_json):
    urls = []
    if 'genbank_accession' in obj_json:
        urls.append({'display_name': obj_json['genbank_accession'],
                     'link': 'http://www.ncbi.nlm.nih.gov/nuccore/' + obj_json['genbank_accession'],
                     'source': {'display_name': 'GenBank-EMBL-DDBJ'},
                     'url_type': 'External'})
    return urls


def load_reference_contig(bud_contig):
    from src.sgd.model.bud.sequence import Sequence, Feat_Location

    if bud_contig.type == 'chromosome' or bud_contig.type == 'plasmid':

        sequence = [x for x in bud_contig.sequences if x.is_current == 'Y'][0]
        feat_locations = [x for x in sequence.feat_locations if x.is_current == 'Y']

        display_name = 'Chromosome ' + (bud_contig.name if bud_contig.name not in number_to_roman else number_to_roman[bud_contig.name])
        releases = [] if len(sequence.feat_locations) == 0 else [x.release for x in sequence.feat_locations[0].featlocation_rels]
        centromeres = [x.child for x in bud_contig.children if x.child.type == 'centromere']
        obj_json = {'display_name': display_name,
                    'source': {'display_name': 'SGD'},
                    'taxonomy': {'display_name': 'Saccharomyces cerevisiae S288c'},
                    'residues': sequence.residues,
                    'is_chromosome': True,
                    'bud_id': bud_contig.id,
                    'seq_version': str(sequence.seq_version),
                    'date_created': str(bud_contig.date_created),
                    'created_by': bud_contig.created_by}

        if len(releases) > 0:
            obj_json['genomerelease'] = {'genome_release': releases[0].genome_release}

        if len(feat_locations) > 0:
            obj_json['coord_version'] = str(feat_locations[0].coord_version)

        if len(centromeres) > 0:
            feat_location = [x for x in centromeres[0].feat_locations if x.is_current == 'Y'][0]
            obj_json['centromere_start'] = feat_location.min_coord
            obj_json['centromere_end'] = feat_location.max_coord

        if display_name in s288c_chromosome_to_genbank__refseq_id:
            genbank_accession, refseq_id = s288c_chromosome_to_genbank__refseq_id[display_name]
            obj_json['genbank_accession'] = genbank_accession
            obj_json['refseq_id'] = refseq_id

        obj_json['urls'] = load_contig_urls(obj_json)
        return obj_json
    else:
        return None


def load_extensions(feature, annotation_start, annotation_end):
    extensions = []
    for child_rel in feature.children:
        child = child_rel.child
        if child.type != 'TF_binding_site':
            bud_location = [x for x in child.feat_locations if x.is_current == 'Y'][0]
            start = bud_location.min_coord
            end = bud_location.max_coord

            locus = None
            if child.type == 'ORF' or child.type == 'rRNA':
                display_name = child.name if child.gene_name is None else child.name + '(' + child.gene_name + ')'
                locus = {'sgdid': child.dbxref_id}
            else:
                display_name = bud_location.feature.type

            if bud_location.strand != '-':
                obj_json = {
                    'extension_type': child.type,
                    'display_name': display_name,
                    'relative_start_index': start - annotation_start + 1,
                    'relative_end_index': end - annotation_start + 1,
                    'chromosomal_start_index': start,
                    'chromosomal_end_index': end,
                    'seq_version': str(bud_location.sequence.seq_version),
                    'coord_version': str(bud_location.coord_version),
                }
            else:
                obj_json = {
                    'extension_type': child.type,
                    'display_name': display_name,
                    'relative_start_index': annotation_end - end + 1,
                    'relative_end_index': annotation_end - start + 1,
                    'chromosomal_start_index': end,
                    'chromosomal_end_index': start,
                    'seq_version': str(bud_location.sequence.seq_version),
                    'coord_version': str(bud_location.coord_version),
                }

            if locus is not None:
                obj_json['locus'] = locus

            extensions.append(obj_json)
    return extensions


def dnasequenceannotation_starter(bud_session_maker):
    from src.sgd.model.bud.sequence import Feat_Location

    #Load S288C from bud
    bud_session = bud_session_maker()

    id_to_contig = dict()

    for bud_location in bud_session.query(Feat_Location).options(joinedload('feature')).all():
        if bud_location.is_current == 'Y' and bud_location.feature.type not in non_locus_feature_types:
            releases = [x.release for x in bud_location.featlocation_rels]

            contig = bud_location.feature
            while len(bud_location.feature.parents) > 0 and bud_location.feature.parents[0].parent.id != contig.id:
                contig = bud_location.feature.parents[0].parent

            contig_id = contig.id
            if contig_id in id_to_contig:
                contig = id_to_contig[contig_id]
            else:
                contig = load_reference_contig(contig)
                id_to_contig[contig_id] = contig

            obj_json = {'source': {'display_name': 'SGD'},
                   'taxonomy': {'display_name': 'Saccharomyces cerevisiae S288c'},
                   'dbentity': {'sgdid': bud_location.feature.dbxref_id},
                   'contig': contig,
                   'dna_type': 'GENOMIC',
                   'residues': bud_location.sequence.residues,
                   'start_index': bud_location.min_coord,
                   'end_index': bud_location.max_coord,
                   'strand': bud_location.strand,
                   'seq_version': str(bud_location.sequence.seq_version),
                   'coord_version': str(bud_location.coord_version),
                   'bud_id': bud_location.id,
                   'date_created': str(bud_location.date_created),
                   'created_by': bud_location.created_by}

            if len(releases) > 0:
                obj_json['genomerelease'] = {'genome_release': releases[0].genome_release}

            obj_json['extensions'] = load_extensions(bud_location.feature, obj_json['start_index'], obj_json['end_index'])

            yield obj_json

    # #Multigene Locii
    # for feature in bud_session.query(Feature).filter_by(type='gene_group').all():
    #     subfeature_relations = bud_session.query(FeatRel).filter_by(parent_id=feature.id).all()
    #     locations = bud_session.query(Feat_Location).filter(Feat_Location.feature_id.in_([x.child_id for x in subfeature_relations])).filter_by(is_current='Y')
    #     min_coord = min([x.min_coord for x in locations])
    #     max_coord = max([x.max_coord for x in locations])
    #     contig = feature_id_to_contig[subfeature_relations[0].child_id]
    #     strand = locations[0].strand
    #     if strand == '-':
    #         residues = reverse_complement(contig.residues[min_coord-1:max_coord])
    #     else:
    #         residues = contig.residues[min_coord-1:max_coord]
    #
    #     yield {'source': key_to_source['SGD'],
    #            'strain': key_to_strain['S288C'],
    #            'locus': id_to_bioentity[feature.id],
    #            'dna_type': 'GENOMIC',
    #            'residues': residues,
    #            'contig': contig,
    #            'start': min_coord,
    #            'end': max_coord,
    #            'strand': strand}
    # bud_session.close()
    #
    #
    # for coding_seq_file in coding_sequence_filenames:
    #     f = open(coding_seq_file, 'r')
    #     for bioentity_name, residues in get_sequence_library_fsa(f).iteritems():
    #         bioentity_key = (bioentity_name, 'LOCUS')
    #         if bioentity_key[0] == 'tS(GCU)L':
    #             bioentity_key = ('tX(XXX)L', 'LOCUS')
    #         elif bioentity_key[0] == 'tT(XXX)Q2':
    #             bioentity_key = ('tT(UAG)Q2', 'LOCUS')
    #
    #         if bioentity_key in key_to_bioentity:
    #             yield {'source': key_to_source['SGD'],
    #                    'strain': key_to_strain['S288C'],
    #                    'locus': key_to_bioentity[bioentity_key],
    #                    'dna_type': 'CODING',
    #                    'residues': residues}
    #         else:
    #             print 'Bioentity not found: ' + str(bioentity_key)
    #
    #     f.close()




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


# --------------------- Convert DNA Sequence Evidence ---------------------
def make_new_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename):
    print strain_key
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Contig
    def dna_sequence_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in nex_session.query(Contig).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        f = open(sequence_filename, 'r')
        sequence_library = get_dna_sequence_library(f, remove_spaces=True)
        f.close()

        f = open(sequence_filename, 'r')
        for row in f:
            pieces = row.split(' ')
            if len(pieces) >= 9 and not row.startswith('>'):
                parent_id = pieces[0]
                start = int(pieces[3])
                end = int(pieces[4])
                strand = pieces[6]
                infos = pieces[8].split(',')
                residues = get_sequence(parent_id, start, end, strand, sequence_library)
                class_type = pieces[2]

                if class_type != 'CDS':
                    for info in infos:
                        #bioentity_format_name, species, ref_chromosome, ref_start, ref_end, bioentity_display_name, evalue, similarity_score

                        bioentity_key = (infos[0].strip(), 'LOCUS')
                        contig_key = (parent_id.split('|')[3], 'CONTIG')

                        if bioentity_key in key_to_bioentity and contig_key in key_to_bioitem and residues is not None:
                            yield {'source': key_to_source['SGD'],
                                            'strain': key_to_strain[strain_key],
                                            'locus': key_to_bioentity[bioentity_key],
                                            'dna_type': 'GENOMIC',
                                            'residues': residues,
                                            'contig': key_to_bioitem[contig_key],
                                            'start': start,
                                            'end': end,
                                            'strand': strand}
                        else:
                            print 'Bioentity or contig or residues not found: ' + str(bioentity_key) + ' ' + str(contig_key)
                            yield None
        f.close()

        f = open(coding_sequence_filename, 'r')
        for bioentity_name, residues in get_sequence_library_fsa(f).iteritems():
            bioentity_key = (bioentity_name, 'LOCUS')

            if bioentity_key in key_to_bioentity:
                yield {'source': key_to_source['SGD'],
                            'strain': key_to_strain[strain_key],
                            'locus': key_to_bioentity[bioentity_key],
                            'dna_type': 'CODING',
                            'residues': residues}
            else:
                print 'Bioentity not found: ' + str(bioentity_key)

        f.close()

        nex_session.close()
    return dna_sequence_evidence_starter

# --------------------- Convert DNA Sequence Evidence ---------------------
def make_dna_sequence_evidence_starter(nex_session_maker, strain_key, sequence_filename, coding_sequence_filename):
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Contig
    def dna_sequence_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in nex_session.query(Contig).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

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
                if len(pieces) == 9:
                    parent_id = pieces[0]
                    start = int(pieces[3])
                    end = int(pieces[4])
                    strand = pieces[6]
                    info = get_info(pieces[8])
                    class_type = pieces[2]
                    residues = get_sequence(parent_id, start, end, strand, sequence_library)

                    if 'Name' in info and 'Parent' not in info:
                        bioentity_key = (info['Name'].strip().replace('%28', "(").replace('%29', ")"), 'LOCUS')
                        if bioentity_key[0].endswith('_mRNA'):
                            bioentity_key = (bioentity_key[0][:-5], 'LOCUS')
                        elif bioentity_key[0] == 'tS(GCU)L':
                            bioentity_key = ('tX(XXX)L', 'LOCUS')
                        elif bioentity_key[0] == 'tT(XXX)Q2':
                            bioentity_key = ('tT(UAG)Q2', 'LOCUS')

                        if sequence_filename == "src/sgd/convert/data/strains/scerevisiae_2-micron.gff":
                            print bioentity_key
                        contig_key = (strain_key + '_' + parent_id, 'CONTIG')

                        if bioentity_key in key_to_bioentity and contig_key in key_to_bioitem and key_to_bioentity[bioentity_key].locus_type != 'plasmid':
                            yield {'source': key_to_source['SGD'],
                                        'strain': key_to_strain[strain_key],
                                        'locus': key_to_bioentity[bioentity_key],
                                        'dna_type': 'GENOMIC',
                                        'residues': residues,
                                        'contig': key_to_bioitem[contig_key],
                                        'start': start,
                                        'end': end,
                                        'strand': strand}
                        else:
                            print 'Bioentity or contig not found: ' + str(bioentity_key) + ' ' + str(contig_key)
                            yield None
            f.close()

        coding_sequence_filenames = []
        if isinstance(coding_sequence_filename, list):
            coding_sequence_filenames = coding_sequence_filename
        elif coding_sequence_filename is not None:
            coding_sequence_filenames.append(coding_sequence_filename)

        for coding_seq_file in coding_sequence_filenames:
            f = open(coding_seq_file, 'r')
            for bioentity_name, residues in get_sequence_library_fsa(f).iteritems():
                bioentity_key = (bioentity_name, 'LOCUS')
                if bioentity_key[0] == 'tS(GCU)L':
                    bioentity_key = ('tX(XXX)L', 'LOCUS')
                elif bioentity_key[0] == 'tT(XXX)Q2':
                    bioentity_key = ('tT(UAG)Q2', 'LOCUS')

                if bioentity_key in key_to_bioentity:
                    yield {'source': key_to_source['SGD'],
                            'strain': key_to_strain[strain_key],
                            'locus': key_to_bioentity[bioentity_key],
                            'dna_type': 'CODING',
                            'residues': residues}
                else:
                    print 'Bioentity not found: ' + str(bioentity_key)

            f.close()

        nex_session.close()
    return dna_sequence_evidence_starter

def get_info(data):
    info = {}
    for entry in data.split(';'):
        pieces = entry.split('=')
        if len(pieces) == 2:
            info[pieces[0]] = pieces[1]
    return info



def make_kb_sequence_starter(nex_session_maker):
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    from src.sgd.model.nex.bioitem import Contig
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Bioentity
    def kb_sequence_starter():
        nex_session = nex_session_maker()

        id_to_contig = dict([(x.id, x) for x in nex_session.query(Contig).all()])
        id_to_source = dict([(x.id, x) for x in nex_session.query(Source).all()])
        id_to_strain = dict([(x.id, x) for x in nex_session.query(Strain).all()])
        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])

        for dnasequenceevidence in nex_session.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').all():
            contig = id_to_contig[dnasequenceevidence.contig_id]
            min_coord = max(1, dnasequenceevidence.start - 1000)
            max_coord = min(len(contig.residues), dnasequenceevidence.end + 1000)
            residues = contig.residues[min_coord - 1:max_coord]
            if dnasequenceevidence.strand == '-':
                residues = reverse_complement(residues)
            yield {'source': id_to_source[dnasequenceevidence.source_id],
                        'strain': id_to_strain[dnasequenceevidence.strain_id],
                        'locus': id_to_bioentity[dnasequenceevidence.locus_id],
                        'dna_type': '1KB',
                        'residues': residues,
                        'contig': contig,
                        'start': min_coord,
                        'end': max_coord,
                        'strand': dnasequenceevidence.strand}

        nex_session.close()
    return kb_sequence_starter

def make_dna_sequence_tag_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.misc import Strain
    from src.sgd.model.nex.bioitem import Contig
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    from src.sgd.model.bud.feature import FeatRel
    from src.sgd.model.bud.sequence import Feat_Location
    def dna_sequence_tag_starter():
        nex_session = nex_session_maker()
        bud_session = bud_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        feature_id_to_parent = dict([(x.child_id, x.parent_id) for x in bud_session.query(FeatRel).filter_by(relationship_type='part of').all()])
        bioentity_strain_id_to_evidence = dict([((x.locus_id, x.strain_id), x) for x in nex_session.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').filter_by(strain_id=1).all()])
        for bud_location in bud_session.query(Feat_Location).filter(Feat_Location.is_current == 'Y').options(joinedload('sequence'), joinedload('feature')).all():
            if bud_location.sequence.is_current == 'Y' and bud_location.feature.status == 'Active':
                bioentity_id = None if bud_location.feature_id not in feature_id_to_parent else feature_id_to_parent[bud_location.feature_id]
                while bioentity_id is not None and bioentity_id not in id_to_bioentity:
                    if bioentity_id in feature_id_to_parent:
                        bioentity_id = feature_id_to_parent[bioentity_id]
                    else:
                        bioentity_id = None

                if bioentity_id is not None and (bioentity_id, 1) in bioentity_strain_id_to_evidence:
                    evidence = bioentity_strain_id_to_evidence[(bioentity_id, 1)]
                    start = bud_location.min_coord
                    end = bud_location.max_coord
                    bioentity = None
                    if bud_location.feature.type == 'ORF' or bud_location.feature.type == 'rRNA':
                        display_name = bud_location.feature.name if bud_location.feature.gene_name is None else bud_location.feature.name + '(' + bud_location.feature.gene_name + ')'
                        bioentity = id_to_bioentity[bud_location.feature_id]
                    else:
                        display_name = bud_location.feature.type

                    if bud_location.feature.type != 'TF_binding_site':
                        if bud_location.strand != '-':
                            yield {
                                'evidence_id': evidence.id,
                                'class_type': bud_location.feature.type,
                                'display_name': display_name,
                                'relative_start': start - evidence.start + 1,
                                'relative_end': end - evidence.start + 1,
                                'chromosomal_start': start,
                                'chromosomal_end': end,
                                'seq_version': bud_location.sequence.seq_version,
                                'coord_version': bud_location.coord_version,
                                'bioentity': bioentity
                            }
                        else:
                            yield {
                                'evidence_id': evidence.id,
                                'class_type': bud_location.feature.type,
                                'display_name': display_name,
                                'relative_start': evidence.end - end + 1,
                                'relative_end': evidence.end - start + 1,
                                'chromosomal_start': end,
                                'chromosomal_end': start,
                                'seq_version': bud_location.sequence.seq_version,
                                'coord_version': bud_location.coord_version,
                                'bioentity': bioentity
                            }

        #Five prime UTR introns:
        for feat_rel in bud_session.query(FeatRel).filter_by(relationship_type='adjacent_to').all():
            feat_location = bud_session.query(Feat_Location).filter_by(feature_id=feat_rel.child_id).filter_by(is_current='Y').first()
            if (feat_rel.parent_id, 1) in bioentity_strain_id_to_evidence:
                evidence = bioentity_strain_id_to_evidence[(feat_rel.parent_id, 1)]
                start = feat_location.min_coord
                end = feat_location.max_coord
                print feat_location.strand, start, end, start - evidence.start, end - evidence.start
                if feat_location.strand != '-':
                    yield {
                        'evidence_id': evidence.id,
                        'class_type': feat_location.feature.type,
                        'display_name': feat_location.feature.type,
                        'relative_start': start - evidence.start,
                        'relative_end': end - evidence.start,
                        'chromosomal_start': start,
                        'chromosomal_end': end,
                        'seq_version': feat_location.sequence.seq_version,
                        'coord_version': feat_location.coord_version
                    }
                else:
                    yield {
                        'evidence_id': evidence.id,
                        'class_type': feat_location.feature.type,
                        'display_name': feat_location.feature.type,
                        'relative_start': evidence.end - end,
                        'relative_end': evidence.end - start,
                        'chromosomal_start': end,
                        'chromosomal_end': start,
                        'seq_version': feat_location.sequence.seq_version,
                        'coord_version': feat_location.coord_version
                    }

        # #Other strains
        # from src.sgd.convert.from_bud import new_sequence_files
        # for seq_file, coding_file, strain_name in new_sequence_files:
        #     strain_id = key_to_strain[strain_name].id
        #
        #     f = open(seq_file, 'r')
        #     previous_evidence_id = None
        #     previous_end = None
        #     for row in f:
        #         pieces = row.split(' ')
        #         if len(pieces) == 9:
        #             parent_id = pieces[0]
        #             start = int(pieces[3])
        #             end = int(pieces[4])
        #             strand = pieces[6]
        #             infos = pieces[8].split(':')
        #             class_type = pieces[2]
        #
        #             contig_key = (strain_name + '_' + parent_id, 'CONTIG')
        #
        #             if class_type == 'CDS' and contig_key in key_to_contig:
        #                 contig_id = key_to_contig[contig_key].id
        #                 for info in infos:
        #                     #bioentity_format_name, species, ref_chromosome, ref_start, ref_end, bioentity_display_name, evalue, similarity_score
        #                     info_values = info.split(',')
        #
        #                     bioentity_key = (info_values[0].strip(), 'LOCUS')
        #                     if bioentity_key in key_to_bioentity:
        #                         bioentity_id = key_to_bioentity[bioentity_key].id
        #                         if bioentity_id != 0:
        #                             if (bioentity_id, strain_id, contig_id) in bioentity_strain_contig_id_to_evidence:
        #                                 evidence = bioentity_strain_contig_id_to_evidence[(bioentity_id, strain_id, contig_id)]
        #
        #                                 yield {
        #                                         'evidence_id': evidence.id,
        #                                         'class_type': class_type,
        #                                         'display_name': class_type,
        #                                         'relative_start': start - evidence.start + 1,
        #                                         'relative_end': end - evidence.start + 1,
        #                                         'chromosomal_start': start,
        #                                         'chromosomal_end': end,
        #                                         'seq_version': None,
        #                                         'coord_version': None
        #                                 }
        #
        #                             else:
        #                                 print 'Evidence not found: ' + str((bioentity_id, strain_id))
        #                                 yield None
        #                     else:
        #                         print 'Bioentity not found: ' + str(bioentity_key)
        #                         yield None
        #    f.close()

        nex_session.close()
        bud_session.close()
    return dna_sequence_tag_starter

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



        nex_session.close()
        bud_session.close()
    return contig_starter


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, dnasequenceannotation_starter, 'dnasequenceannotation', lambda x: (x['dbentity']['sgdid'], x['taxonomy']['display_name'], x['dna_type']))


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
