'''
Created on Sep 23, 2013

@author: kpaskov
'''
from convert_utils import create_or_update
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys

sequence_files = [("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/saccharomyces_cerevisiae_R64-1-1_20110208.gff", 'S288C'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/CEN.PK113-7D_AEHG00000000.gff", 'CEN.PK'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/W303_ALAV00000000.gff", 'W303'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/AWRI1631_ABSV01000000.gff", 'AWRI1631'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/AWRI796_ADVS01000000.gff", 'AWRI796'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/BY4741_Toronto_2012.gff", 'BY4741'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/BY4742_Toronto_2012.gff", 'BY4742'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/CBS7960_AEWL01000000.gff", 'CBS7960'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/CLIB215_AEWP01000000.gff", 'CLIB215'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/CLIB324_AEWM01000000.gff", 'CLIB324'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/CLIB382_AFDG01000000.gff", 'CLIB382'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/EC1118_PRJEA37863.gff", 'EC1118'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/EC9-8_AGSJ01000000.gff", 'EC9-8'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/FL100_AEWO01000000.gff", 'FL100'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/FostersB_AEHH01000000.gff", 'FostersB'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/FostersO_AEEZ01000000.gff", 'FostersO'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/JAY291_ACFL01000000.gff", 'JAY291'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/Kyokai7_BABQ01000000.gff", 'Kyokai7'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/LalvinQA23_ADVV01000000.gff", 'LalvinQA23'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/M22_ABPC01000000.gff", 'M22'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/PW5_AFDC01000000.gff", 'PW5'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/RM11-1a_AAEG01000000.gff", 'RM11-1a'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/Sigma1278b_ACVY01000000.gff", 'Sigma1278b'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/T7_AFDE01000000.gff", 'T7'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/T73_AFDF01000000.gff", 'T73'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/UC5_AFDD01000000.gff", 'UC5'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/Vin13_ADXC01000000.gff", 'VIN13'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/VL3_AEJS01000000.gff", 'VL3'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/Y10_AEWK01000000.gff", 'Y10'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/YJM269_AEWN01000000.gff", 'YJM269'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/YJM789_AAFW02000000.gff", 'YJM789'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/YPS163_ABPD01000000.gff", 'YPS163'),
                      ("/Users/kpaskov/Downloads/S288C_reference_genome_R64-1-1_20110203/ZTW1_AMDD00000000.gff", 'ZTW1')]

"""
--------------------- Convert DNA Sequence ---------------------
"""
def get_dna_sequence_library(gff3_file):
    id_to_sequence = {}
    on_sequence = False
    current_id = None
    current_sequence = []
    for line in gff3_file:
        line = line.replace("\r\n","").replace("\n", "")
        if not on_sequence and line == '##FASTA':
            on_sequence = True
        elif line.startswith('>'):
            if current_id is not None:
                id_to_sequence[current_id] = ''.join(current_sequence)
            current_id = line[1:]
            current_sequence = []
        elif on_sequence:
            current_sequence.append(line)

    if current_id is not None:
        id_to_sequence[current_id] = ''.join(current_sequence)

    return id_to_sequence

def reverse_complement(residues):
    basecomplement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 't': 'a', 'a': 't', 'c': 'g', 'g': 'c', 'n': 'n',
                      'W': 'W*', 'Y': 'R', 'R': 'Y', 'S': 'S*', 'K':'M', 'M':'K', 'B':'V', 'D':'H', 'H':'D', 'V':'B', 'N':'N'}
    letters = list(residues)
    letters = [basecomplement[base] for base in letters][::-1]
    return ''.join(letters)

sequence_class_types = {'gene', 'ARS', 'tRNA', 'ncRNA', 'mRNA', 'snoRNA', 'rRNA'}

def create_dna_sequence(row, sequence_library):
    from model_new_schema.sequence import Dnasequence
    pieces = row.split('\t')
    if len(pieces) == 9:
        parent_id = pieces[0]
        start = int(pieces[3])
        end = int(pieces[4])
        strand = pieces[6]
        class_type = pieces[2]
        if parent_id in sequence_library:
            if class_type in sequence_class_types:
                residues = sequence_library[parent_id][start-1:end]
                if strand == '-':
                    residues = reverse_complement(residues)
                return [Dnasequence(residues)]
        else:
            print 'Parent not found: ' + parent_id
    return []

def convert_strain_dna_sequence(filename, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    f = open(filename, 'r')
    for old_obj in f:
       #Convert old objects into new ones
        newly_created_objs = create_dna_sequence(old_obj, sequence_library)

        if newly_created_objs is not None:
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

                    already_seen.add(unique_key)

    #f.close()
    output_creator.finished()
    new_session.commit()

def convert_dna_sequence(new_session_maker):
    from model_new_schema.sequence import Dnasequence
    
    log = logging.getLogger('convert.sequence.sequence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = []

        #Grab current objects
        current_objs = new_session.query(Dnasequence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_dna_sequence(filename, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()
                    
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        
    log.info('complete')

"""
--------------------- Convert DNA Sequence Evidence ---------------------
"""

def get_info(data):
    info = {}
    for entry in data.split(';'):
        pieces = entry.split('=')
        if len(pieces) == 2:
            info[pieces[0]] = pieces[1]
    return info

def create_dna_evidence(row, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library):
    from model_new_schema.evidence import Sequenceevidence
    source = key_to_source['SGD']
    pieces = row.split('\t')
    if len(pieces) == 9:
        parent_id = pieces[0]
        start = int(pieces[3])
        end = int(pieces[4])
        strand = pieces[6]
        info = get_info(pieces[8])
        class_type = pieces[2]
        new_sequence = create_dna_sequence(row, sequence_library)
        sequence_key = None if len(new_sequence) != 1 else new_sequence[0].unique_key()

        if 'Name' in info and class_type in sequence_class_types:
            if sequence_key is not None and sequence_key in key_to_sequence:
                bioentity_key = (info['Name'], 'LOCUS')
                contig = key_to_sequence[(strain.format_name + '_' + parent_id, 'CONTIG')]
                if bioentity_key in key_to_bioentity:
                    return [Sequenceevidence(source, strain, key_to_bioentity[bioentity_key], key_to_sequence[sequence_key], contig, start, end, strand, None, None)]
            else:
                print 'Sequence not found: ' + str(sequence_key)
    return []

def convert_strain_dna_evidence(filename, strain, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids, key_to_source, key_to_sequence, key_to_bioentity):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    f = open(filename, 'r')
    for old_obj in f:
        #Convert old objects into new ones
        newly_created_objs = create_dna_evidence(old_obj, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library)

        if newly_created_objs is not None:
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen.add(unique_key)

    f.close()
    output_creator.finished()
    new_session.commit()

def convert_dna_evidence(new_session_maker):
    from model_new_schema.evidence import Sequenceevidence
    from model_new_schema.evelements import Source, Strain
    from model_new_schema.sequence import Sequence
    from model_new_schema.bioentity import Bioentity

    log = logging.getLogger('convert.sequence.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['start', 'end', 'strand', 'contig_id']

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_sequence = dict([(x.unique_key(), x) for x in new_session.query(Sequence).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        #Grab current objects
        current_objs = new_session.query(Sequenceevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_dna_evidence(filename, key_to_strain[strain], values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids, key_to_source, key_to_sequence, key_to_bioentity)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

    log.info('complete')

"""
--------------------- DNA Convert Sequence Label ---------------------
"""

def create_dna_sequence_label(row, parent_id_to_evidence):
    from model_new_schema.evidence import SequenceLabel
    pieces = row.split('\t')
    if len(pieces) == 9:
        class_type = pieces[2]
        start = int(pieces[3])
        end = int(pieces[4])
        phase = pieces[7]
        strand = pieces[6]
        info = get_info(pieces[8])

        if 'Parent' in info:
            parent_id = info['Parent']
            if parent_id in parent_id_to_evidence:
                evidence = parent_id_to_evidence[parent_id]
                if strand == '-':
                    relative_start = evidence.end - end + 1
                    relative_end = evidence.end - start + 1
                    chromosomal_start = end
                    chromosomal_end = start
                else:
                    relative_start = start - evidence.start + 1
                    relative_end = end - evidence.start + 1
                    chromosomal_start = start
                    chromosomal_end = end
                return [SequenceLabel(evidence, class_type, relative_start, relative_end, chromosomal_start, chromosomal_end, phase, None, None)]
    return []

def get_parent_id_to_dna_evidence(f, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library, key_to_evidence):
    parent_id_to_evidence = {}
    for line in f:
        pieces = line.split('\t')
        if len(pieces) == 9:
            info = get_info(pieces[8])
            evidence = create_dna_evidence(line, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library)
            if len(evidence) == 1 and 'ID' in info:
                parent_id_to_evidence[info['ID']] = key_to_evidence[evidence[0].unique_key()]
    return parent_id_to_evidence


def convert_strain_dna_sequence_label(filename, strain, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids, key_to_source, key_to_sequence, key_to_bioentity, key_to_evidence):
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    f = open(filename, 'r')
    parent_id_to_evidence = get_parent_id_to_dna_evidence(f, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library, key_to_evidence)
    f.close()

    f = open(filename, 'r')
    for old_obj in f:
        #Convert old objects into new ones
        newly_created_objs = create_dna_sequence_label(old_obj, parent_id_to_evidence)

        if newly_created_objs is not None:
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen.add(unique_key)

    f.close()
    output_creator.finished()
    new_session.commit()

def convert_dna_sequence_label(new_session_maker):
    from model_new_schema.evidence import Sequenceevidence, SequenceLabel
    from model_new_schema.evelements import Source, Strain
    from model_new_schema.sequence import Dnasequence
    from model_new_schema.bioentity import Bioentity

    log = logging.getLogger('convert.sequence.sequencelabels')
    log.info('begin')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['relative_start', 'relative_end', 'phase']

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_sequence = dict([(x.unique_key(), x) for x in new_session.query(Dnasequence).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
        key_to_evidence = dict([(x.unique_key(), x) for x in new_session.query(Sequenceevidence).all()])

        #Grab current objects
        current_objs = new_session.query(SequenceLabel).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_dna_sequence_label(filename, key_to_strain[strain],
                                      values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids,
                                      key_to_source, key_to_sequence, key_to_bioentity, key_to_evidence)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

    log.info('complete')

"""
--------------------- Convert Protein Sequence ---------------------
"""
#http://www.petercollingridge.co.uk/book/export/html/474
bases = ['t', 'c', 'a', 'g']
codons = [a+b+c for a in bases for b in bases for c in bases]
amino_acids = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
codon_table = dict(zip(codons, amino_acids))

def translate(seq):
    seq = seq.lower().replace('\n', '').replace(' ', '')
    peptide = ''

    for i in xrange(0, len(seq), 3):
        codon = seq[i: i+3]
        amino_acid = codon_table.get(codon, '*')
        if amino_acid != '*':
            peptide += amino_acid
        else:
            break

    return peptide

def create_protein_sequence(dna_sequence):
    from model_new_schema.sequence import Proteinsequence
    return [Proteinsequence(translate(dna_sequence.residues))]

def convert_protein_sequence(new_session_maker):
    from model_new_schema.sequence import Proteinsequence, Dnasequence

    log = logging.getLogger('convert.sequence.sequence')
    log.info('begin')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = []

        #Grab current objects
        current_objs = new_session.query(Proteinsequence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        old_objs = new_session.query(Dnasequence).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_protein_sequence(old_obj)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in already_seen:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)

                        already_seen.add(unique_key)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

    log.info('complete')

"""
--------------------- Convert Protein Sequence Evidence ---------------------
"""


def create_protein_evidence(seqevidence, key_to_source, id_to_bioentity, key_to_sequence, id_to_strain):
    from model_new_schema.evidence import Sequenceevidence
    source = key_to_source['SGD']
    sequence = key_to_sequence[create_protein_sequence(seqevidence.sequence)[0].unique_key()]
    bioentity = id_to_bioentity[seqevidence.bioentity_id]
    strain = id_to_strain[seqevidence.strain_id]

    return [Sequenceevidence(source, strain, bioentity, sequence, 1, sequence.length, seqevidence.strand, None, None)]

def convert_protein_evidence(new_session_maker):
    from model_new_schema.evidence import Sequenceevidence
    from model_new_schema.evelements import Source, Strain
    from model_new_schema.sequence import Dnasequence
    from model_new_schema.bioentity import Bioentity

    log = logging.getLogger('convert.sequence.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['start', 'end', 'strand']

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_sequence = dict([(x.unique_key(), x) for x in new_session.query(Dnasequence).all()])
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(Bioentity).all()])
        id_to_strain = dict([(x.id, x) for x in new_session.query(Strain).all()])

        #Grab current objects
        current_objs = new_session.query(Sequenceevidence).options(joinedload(Sequenceevidence.sequence)).filter(Sequenceevidence.sequence.class_type == 'PROTEIN').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        old_objs = new_session.query(Sequenceevidence).options(joinedload(Sequenceevidence.sequence)).filter(Sequenceevidence.sequence.class_type == 'DNA').all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_protein_evidence(old_obj, key_to_source, id_to_bioentity, key_to_sequence, id_to_strain)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in already_seen:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        already_seen.add(unique_key)
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

    log.info('complete')

"""
--------------------- Convert Contig Sequence ---------------------
"""

def create_contig(sequence_library, strain):
    from model_new_schema.sequence import Contig
    return [Contig(x, y, strain) for x, y in sequence_library.iteritems()]

def convert_strain_contig(filename, strain, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    newly_created_objs = create_contig(sequence_library, strain)

    if newly_created_objs is not None:
        #Edit or add new objects
        for newly_created_obj in newly_created_objs:
            unique_key = newly_created_obj.unique_key()
            if unique_key not in already_seen:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)

                already_seen.add(unique_key)

    output_creator.finished()
    new_session.commit()

def convert_contig(new_session_maker):
    from model_new_schema.sequence import Contig
    from model_new_schema.evelements import Strain

    log = logging.getLogger('convert.sequence.contig')
    log.info('begin')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['display_name', 'residues']

        #Grab current objects
        current_objs = new_session.query(Contig).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_contig(filename, key_to_strain[strain], values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

    log.info('complete')
    
"""
---------------------Convert------------------------------
"""  


def convert(new_session_maker):

    #convert_contig(new_session_maker)

    #convert_dna_sequence(new_session_maker)
    convert_dna_evidence(new_session_maker)
    #convert_dna_sequence_label(new_session_maker)

    #convert_protein_sequence(new_session_maker)
    #convert_protein_evidence(new_session_maker)