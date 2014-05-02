import re

import evelements
import reference
import bioconcept
import bioitem


__author__ = 'kpaskov'

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

sequence_files = [("src/sgd/convert/data/strains/saccharomyces_cerevisiae.gff", "src/sgd/convert/data/strains/orf_coding_all_R64-1-1_20110203.fasta", 'S288C'),
                      ("src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000.gff", "src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000_cds.fsa.txt", 'CENPK'),
                      ("src/sgd/convert/data/strains/W303_ALAV00000000.gff", "src/sgd/convert/data/strains/W303_ALAV00000000_cds.fsa.txt", 'W303'),
                      ("src/sgd/convert/data/strains/AWRI1631_ABSV01000000.gff", "src/sgd/convert/data/strains/AWRI1631_ABSV01000000_cds.fsa.txt", 'AWRI1631'),
                      ("src/sgd/convert/data/strains/AWRI796_ADVS01000000.gff", "src/sgd/convert/data/strains/AWRI796_ADVS01000000_cds.fsa.txt", 'AWRI796'),
                      ("src/sgd/convert/data/strains/BY4741_Toronto_2012.gff", "src/sgd/convert/data/strains/BY4741_Toronto_2012_cds.fsa.txt", 'BY4741'),
                      ("src/sgd/convert/data/strains/BY4742_Toronto_2012.gff", "src/sgd/convert/data/strains/BY4742_Toronto_2012_cds.fsa.txt", 'BY4742'),
                      ("src/sgd/convert/data/strains/CBS7960_AEWL01000000.gff", "src/sgd/convert/data/strains/CBS7960_AEWL01000000_cds.fsa.txt", 'CBS7960'),
                      ("src/sgd/convert/data/strains/CLIB215_AEWP01000000.gff", "src/sgd/convert/data/strains/CLIB215_AEWP01000000_cds.fsa.txt", 'CLIB215'),
                      ("src/sgd/convert/data/strains/CLIB324_AEWM01000000.gff", "src/sgd/convert/data/strains/CLIB324_AEWM01000000_cds.fsa.txt", 'CLIB324'),
                      ("src/sgd/convert/data/strains/CLIB382_AFDG01000000.gff", "src/sgd/convert/data/strains/CLIB382_AFDG01000000_cds.fsa.txt", 'CLIB382'),
                      ("src/sgd/convert/data/strains/EC1118_PRJEA37863.gff", "src/sgd/convert/data/strains/EC1118_PRJEA37863_cds.fsa.txt", 'EC1118'),
                      ("src/sgd/convert/data/strains/EC9-8_AGSJ01000000.gff", "src/sgd/convert/data/strains/EC9-8_AGSJ01000000_cds.fsa.txt", 'EC9-8'),
                      ("src/sgd/convert/data/strains/FL100_AEWO01000000.gff", "src/sgd/convert/data/strains/FL100_AEWO01000000_cds.fsa.txt", 'FL100'),
                      ("src/sgd/convert/data/strains/FostersB_AEHH01000000.gff", "src/sgd/convert/data/strains/FostersB_AEHH01000000_cds.fsa.txt", 'FostersB'),
                      ("src/sgd/convert/data/strains/FostersO_AEEZ01000000.gff", "src/sgd/convert/data/strains/FostersO_AEEZ01000000_cds.fsa.txt", 'FostersO'),
                      ("src/sgd/convert/data/strains/JAY291_ACFL01000000.gff", "src/sgd/convert/data/strains/JAY291_ACFL01000000_cds.fsa.txt", 'JAY291'),
                      ("src/sgd/convert/data/strains/Kyokai7_BABQ01000000.gff", "src/sgd/convert/data/strains/Kyokai7_BABQ01000000_cds.fsa.txt", 'Kyokai7'),
                      ("src/sgd/convert/data/strains/LalvinQA23_ADVV01000000.gff", "src/sgd/convert/data/strains/LalvinQA23_ADVV01000000_cds.fsa.txt", 'LalvinQA23'),
                      ("src/sgd/convert/data/strains/M22_ABPC01000000.gff", "src/sgd/convert/data/strains/M22_ABPC01000000_cds.fsa.txt", 'M22'),
                      ("src/sgd/convert/data/strains/PW5_AFDC01000000.gff", "src/sgd/convert/data/strains/PW5_AFDC01000000_cds.fsa.txt", 'PW5'),
                      ("src/sgd/convert/data/strains/RM11-1a_AAEG01000000.gff", "src/sgd/convert/data/strains/RM11-1a_AAEG01000000_cds.fsa.txt", 'RM11-1a'),
                      ("src/sgd/convert/data/strains/Sigma1278b_ACVY01000000.gff", "src/sgd/convert/data/strains/Sigma1278b_ACVY01000000_cds.fsa.txt", 'Sigma1278b'),
                      ("src/sgd/convert/data/strains/T7_AFDE01000000.gff", "src/sgd/convert/data/strains/T7_AFDE01000000_cds.fsa.txt", 'T7'),
                      ("src/sgd/convert/data/strains/T73_AFDF01000000.gff", "src/sgd/convert/data/strains/T73_AFDF01000000_cds.fsa.txt", 'T73'),
                      ("src/sgd/convert/data/strains/UC5_AFDD01000000.gff", "src/sgd/convert/data/strains/UC5_AFDD01000000_cds.fsa.txt", 'UC5'),
                      ("src/sgd/convert/data/strains/Vin13_ADXC01000000.gff", "src/sgd/convert/data/strains/Vin13_ADXC01000000_cds.fsa.txt", 'VIN13'),
                      ("src/sgd/convert/data/strains/VL3_AEJS01000000.gff", "src/sgd/convert/data/strains/VL3_AEJS01000000_cds.fsa.txt", 'VL3'),
                      ("src/sgd/convert/data/strains/Y10_AEWK01000000.gff", "src/sgd/convert/data/strains/Y10_AEWK01000000_cds.fsa.txt", 'Y10'),
                      ("src/sgd/convert/data/strains/YJM269_AEWN01000000.gff", "src/sgd/convert/data/strains/YJM269_AEWN01000000_cds.fsa.txt", 'YJM269'),
                      ("src/sgd/convert/data/strains/YJM789_AAFW02000000.gff", "src/sgd/convert/data/strains/YJM789_AAFW02000000_cds.fsa.txt", 'YJM789'),
                      ("src/sgd/convert/data/strains/YPS163_ABPD01000000.gff", "src/sgd/convert/data/strains/YPS163_ABPD01000000_cds.fsa.txt", 'YPS163'),
                      ("src/sgd/convert/data/strains/ZTW1_AMDD00000000.gff", "src/sgd/convert/data/strains/ZTW1_AMDD00000000_cds.fsa.txt", 'ZTW1')]

protein_sequence_files = [("src/sgd/convert/data/strains/orf_trans_all_R64-1-1_20110203.fasta", 'S288C'),
                      ("src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000_pep.fsa.txt", 'CENPK'),
                      ("src/sgd/convert/data/strains/W303_ALAV00000000_pep.fsa.txt", 'W303'),
                      ("src/sgd/convert/data/strains/AWRI1631_ABSV01000000_pep.fsa.txt", 'AWRI1631'),
                      ("src/sgd/convert/data/strains/AWRI796_ADVS01000000_pep.fsa.txt", 'AWRI796'),
                      ("src/sgd/convert/data/strains/BY4741_Toronto_2012_pep.fsa.txt", 'BY4741'),
                      ("src/sgd/convert/data/strains/BY4742_Toronto_2012_pep.fsa.txt", 'BY4742'),
                      ("src/sgd/convert/data/strains/CBS7960_AEWL01000000_pep.fsa.txt", 'CBS7960'),
                      ("src/sgd/convert/data/strains/CLIB215_AEWP01000000_pep.fsa.txt", 'CLIB215'),
                      ("src/sgd/convert/data/strains/CLIB324_AEWM01000000_pep.fsa.txt", 'CLIB324'),
                      ("src/sgd/convert/data/strains/CLIB382_AFDG01000000_pep.fsa.txt", 'CLIB382'),
                      ("src/sgd/convert/data/strains/EC1118_PRJEA37863_pep.fsa.txt", 'EC1118'),
                      ("src/sgd/convert/data/strains/EC9-8_AGSJ01000000_pep.fsa.txt", 'EC9-8'),
                      ("src/sgd/convert/data/strains/FL100_AEWO01000000_pep.fsa.txt", 'FL100'),
                      ("src/sgd/convert/data/strains/FostersB_AEHH01000000_pep.fsa.txt", 'FostersB'),
                      ("src/sgd/convert/data/strains/FostersO_AEEZ01000000_pep.fsa.txt", 'FostersO'),
                      ("src/sgd/convert/data/strains/JAY291_ACFL01000000_pep.fsa.txt", 'JAY291'),
                      ("src/sgd/convert/data/strains/Kyokai7_BABQ01000000_pep.fsa.txt", 'Kyokai7'),
                      ("src/sgd/convert/data/strains/LalvinQA23_ADVV01000000_pep.fsa.txt", 'LalvinQA23'),
                      ("src/sgd/convert/data/strains/M22_ABPC01000000_pep.fsa.txt", 'M22'),
                      ("src/sgd/convert/data/strains/PW5_AFDC01000000_pep.fsa.txt", 'PW5'),
                      ("src/sgd/convert/data/strains/RM11-1a_AAEG01000000_pep.fsa.txt", 'RM11-1a'),
                      ("src/sgd/convert/data/strains/Sigma1278b_ACVY01000000_pep.fsa.txt", 'Sigma1278b'),
                      ("src/sgd/convert/data/strains/T7_AFDE01000000_pep.fsa.txt", 'T7'),
                      ("src/sgd/convert/data/strains/T73_AFDF01000000_pep.fsa.txt", 'T73'),
                      ("src/sgd/convert/data/strains/UC5_AFDD01000000_pep.fsa.txt", 'UC5'),
                      ("src/sgd/convert/data/strains/Vin13_ADXC01000000_pep.fsa.txt", 'VIN13'),
                      ("src/sgd/convert/data/strains/VL3_AEJS01000000_pep.fsa.txt", 'VL3'),
                      ("src/sgd/convert/data/strains/Y10_AEWK01000000_pep.fsa.txt", 'Y10'),
                      ("src/sgd/convert/data/strains/YJM269_AEWN01000000_pep.fsa.txt", 'YJM269'),
                      ("src/sgd/convert/data/strains/YJM789_AAFW02000000_pep.fsa.txt", 'YJM789'),
                      ("src/sgd/convert/data/strains/YPS163_ABPD01000000_pep.fsa.txt", 'YPS163'),
                      ("src/sgd/convert/data/strains/ZTW1_AMDD00000000_pep.fsa.txt", 'ZTW1')]




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

def get_sequence_library_fsa(fsa_file):
    id_to_sequence = {}
    on_sequence = False
    current_id = None
    current_sequence = []
    for line in fsa_file:
        line = line.replace("\r\n","").replace("\n", "")
        if line.startswith('>'):
            if current_id is not None:
                id_to_sequence[current_id] = ''.join(current_sequence)
            current_id = line[1:]
            if '_' in current_id:
                current_id = current_id[0:current_id.index('_')]
            if ' ' in current_id:
                current_id = current_id[0:current_id.index(' ')]
            current_sequence = []
            on_sequence = True
        elif on_sequence:
            current_sequence.append(line)

    if current_id is not None:
        id_to_sequence[current_id] = ''.join(current_sequence)

    return id_to_sequence

def get_sequence(row, sequence_library):
    pieces = row.split('\t')
    if len(pieces) == 9:
        parent_id = pieces[0]
        start = int(pieces[3])
        end = int(pieces[4])
        strand = pieces[6]
        if parent_id in sequence_library:
            residues = sequence_library[parent_id][start-1:end]
            if strand == '-':
                residues = reverse_complement(residues)
            return residues
        else:
            print 'Parent not found: ' + parent_id
    return None