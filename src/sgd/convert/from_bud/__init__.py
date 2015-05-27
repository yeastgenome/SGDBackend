import re
import json
import datetime

__author__ = 'kpaskov'


def basic_convert(bud_db, nex_db, starter, class_name, key_f):
    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    start = datetime.datetime.now()
    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, bud_db, config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, nex_db, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    already_seen = set()

    accumulated_status = dict()
    warnings_count = 0
    for obj_json in starter(bud_session_maker):
        key = key_f(obj_json)
        print key
        if key in already_seen:
            status = 'Duplicate'
        else:
            response = curate_backend.add_object(class_name, obj_json, update_ok=True)
            status = json.loads(response)['status']
            warnings_count += len(json.loads(response)['warnings'])
            already_seen.add(key)

        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1

    end = datetime.datetime.now()
    print end.date(), 'convert.from_bud.' + class_name, accumulated_status, 'Warnings', warnings_count, 'Start-End/Duration:', \
        datetime.datetime.strftime(start, '%X') + '-' + datetime.datetime.strftime(end, '%X') + '/' + str(end-start)

def remove_nones(obj_json):
    to_be_deleted = set()
    for key, value in obj_json.iteritems():
        if value is None:
            to_be_deleted.add(key)
    for key in to_be_deleted:
        del obj_json[key]
    return obj_json


_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

sequence_files = [
                      #(["src/sgd/convert/data/strains/saccharomyces_cerevisiae.gff", "src/sgd/convert/data/strains/scerevisiae_2-micron.gff"], ["src/sgd/convert/data/strains/orf_coding_all.fasta", "src/sgd/convert/data/strains/rna_coding.fasta"], 'S288C'),
                      #("src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000.gff", "src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000_cds.fsa.txt", 'CENPK'),
                      #("src/sgd/convert/data/strains/W303_ALAV00000000.gff", "src/sgd/convert/data/strains/W303_ALAV00000000_cds.fsa.txt", 'W303'),
                      ("src/sgd/convert/data/strains/AWRI1631_ABSV01000000.gff", "src/sgd/convert/data/strains/AWRI1631_ABSV01000000_cds.fsa.txt", 'AWRI1631'),
                      ("src/sgd/convert/data/strains/AWRI796_ADVS01000000.gff", "src/sgd/convert/data/strains/AWRI796_ADVS01000000_cds.fsa.txt", 'AWRI796'),
                      #("src/sgd/convert/data/strains/BY4741_Toronto_2012.gff", "src/sgd/convert/data/strains/BY4741_Toronto_2012_cds.fsa.txt", 'BY4741'),
                      #("src/sgd/convert/data/strains/BY4742_Toronto_2012.gff", "src/sgd/convert/data/strains/BY4742_Toronto_2012_cds.fsa.txt", 'BY4742'),
                      ("src/sgd/convert/data/strains/CBS7960_AEWL01000000.gff", "src/sgd/convert/data/strains/CBS7960_AEWL01000000_cds.fsa.txt", 'CBS7960'),
                      ("src/sgd/convert/data/strains/CLIB215_AEWP01000000.gff", "src/sgd/convert/data/strains/CLIB215_AEWP01000000_cds.fsa.txt", 'CLIB215'),
                      #("src/sgd/convert/data/strains/CLIB324_AEWM01000000.gff", "src/sgd/convert/data/strains/CLIB324_AEWM01000000_cds.fsa.txt", 'CLIB324'),
                      #("src/sgd/convert/data/strains/CLIB382_AFDG01000000.gff", "src/sgd/convert/data/strains/CLIB382_AFDG01000000_cds.fsa.txt", 'CLIB382'),
                      ("src/sgd/convert/data/strains/EC1118_PRJEA37863.gff", "src/sgd/convert/data/strains/EC1118_PRJEA37863_cds.fsa.txt", 'EC1118'),
                      ("src/sgd/convert/data/strains/EC9-8_AGSJ01000000.gff", "src/sgd/convert/data/strains/EC9-8_AGSJ01000000_cds.fsa.txt", 'EC9-8'),
                      #("src/sgd/convert/data/strains/FL100_AEWO01000000.gff", "src/sgd/convert/data/strains/FL100_AEWO01000000_cds.fsa.txt", 'FL100'),
                      ("src/sgd/convert/data/strains/FostersB_AEHH01000000.gff", "src/sgd/convert/data/strains/FostersB_AEHH01000000_cds.fsa.txt", 'FostersB'),
                      ("src/sgd/convert/data/strains/FostersO_AEEZ01000000.gff", "src/sgd/convert/data/strains/FostersO_AEEZ01000000_cds.fsa.txt", 'FostersO'),
                      ("src/sgd/convert/data/strains/JAY291_ACFL01000000.gff", "src/sgd/convert/data/strains/JAY291_ACFL01000000_cds.fsa.txt", 'JAY291'),
                      ("src/sgd/convert/data/strains/Kyokai7_BABQ01000000.gff", "src/sgd/convert/data/strains/Kyokai7_BABQ01000000_cds.fsa.txt", 'Kyokai7'),
                      ("src/sgd/convert/data/strains/LalvinQA23_ADVV01000000.gff", "src/sgd/convert/data/strains/LalvinQA23_ADVV01000000_cds.fsa.txt", 'LalvinQA23'),
                      #("src/sgd/convert/data/strains/M22_ABPC01000000.gff", "src/sgd/convert/data/strains/M22_ABPC01000000_cds.fsa.txt", 'M22'),
                      ("src/sgd/convert/data/strains/PW5_AFDC01000000.gff", "src/sgd/convert/data/strains/PW5_AFDC01000000_cds.fsa.txt", 'PW5'),
                      #("src/sgd/convert/data/strains/RM11-1a_AAEG01000000.gff", "src/sgd/convert/data/strains/RM11-1a_AAEG01000000_cds.fsa.txt", 'RM11-1a'),
                      ("src/sgd/convert/data/strains/T7_AFDE01000000.gff", "src/sgd/convert/data/strains/T7_AFDE01000000_cds.fsa.txt", 'T7'),
                      #("src/sgd/convert/data/strains/T73_AFDF01000000.gff", "src/sgd/convert/data/strains/T73_AFDF01000000_cds.fsa.txt", 'T73'),
                      ("src/sgd/convert/data/strains/UC5_AFDD01000000.gff", "src/sgd/convert/data/strains/UC5_AFDD01000000_cds.fsa.txt", 'UC5'),
                      ("src/sgd/convert/data/strains/Vin13_ADXC01000000.gff", "src/sgd/convert/data/strains/Vin13_ADXC01000000_cds.fsa.txt", 'VIN13'),
                      ("src/sgd/convert/data/strains/VL3_AEJS01000000.gff", "src/sgd/convert/data/strains/VL3_AEJS01000000_cds.fsa.txt", 'VL3'),
                      #("src/sgd/convert/data/strains/Y10_AEWK01000000.gff", "src/sgd/convert/data/strains/Y10_AEWK01000000_cds.fsa.txt", 'Y10'),
                      ("src/sgd/convert/data/strains/YJM269_AEWN01000000.gff", "src/sgd/convert/data/strains/YJM269_AEWN01000000_cds.fsa.txt", 'YJM269'),
                      ("src/sgd/convert/data/strains/YJM789_AAFW02000000.gff", "src/sgd/convert/data/strains/YJM789_AAFW02000000_cds.fsa.txt", 'YJM789'),
                      #("src/sgd/convert/data/strains/YPS163_ABPD01000000.gff", "src/sgd/convert/data/strains/YPS163_ABPD01000000_cds.fsa.txt", 'YPS163'),
                      ("src/sgd/convert/data/strains/ZTW1_AMDD00000000.gff", "src/sgd/convert/data/strains/ZTW1_AMDD00000000_cds.fsa.txt", 'ZTW1')]



new_sequence_files = [("src/sgd/convert/data/strains/Sigma1278b-10560-6B_JRIQ00000000.gff", 'src/sgd/convert/data/strains/Sigma1278b-10560-6B_JRIQ00000000_cds.fsa', 'Sigma1278b'),
                      ("src/sgd/convert/data/strains/BC187_JRII00000000.gff", "src/sgd/convert/data/strains/BC187_JRII00000000_cds.fsa", 'BC187'),
                      ("src/sgd/convert/data/strains/BY4741_JRIS00000000.gff", "src/sgd/convert/data/strains/BY4741_JRIS00000000_cds.fsa", 'BY4741'),
                      ("src/sgd/convert/data/strains/BY4742_JRIR00000000.gff", "src/sgd/convert/data/strains/BY4742_JRIR00000000_cds.fsa", 'BY4742'),
                      ("src/sgd/convert/data/strains/CEN.PK2-1Ca_JRIV01000000.gff", "src/sgd/convert/data/strains/CEN.PK2-1Ca_JRIV01000000_cds.fsa", 'CENPK'),
                      ("src/sgd/convert/data/strains/D273-10B_JRIY00000000.gff", "src/sgd/convert/data/strains/D273-10B_JRIY00000000_cds.fsa", 'D273-10B'),
                      ("src/sgd/convert/data/strains/DBVPG6044_JRIG00000000.gff", "src/sgd/convert/data/strains/DBVPG6044_JRIG00000000_cds.fsa", 'DBVPG6044'),
                      ("src/sgd/convert/data/strains/FL100_JRIT00000000.gff", "src/sgd/convert/data/strains/FL100_JRIT00000000_cds.fsa", 'FL100'),
                      ("src/sgd/convert/data/strains/FY1679_JRIN00000000.gff", "src/sgd/convert/data/strains/FY1679_JRIN00000000_cds.fsa", 'FY1679'),
                      ("src/sgd/convert/data/strains/JK9-3d_JRIZ00000000.gff", "src/sgd/convert/data/strains/JK9-3d_JRIZ00000000_cds.fsa", 'JK9-3d'),
                      ("src/sgd/convert/data/strains/K11_JRIJ00000000.gff", "src/sgd/convert/data/strains/K11_JRIJ00000000_cds.fsa", 'K11'),
                      ("src/sgd/convert/data/strains/L1528_JRIK00000000.gff", "src/sgd/convert/data/strains/L1528_JRIK00000000_cds.fsa", 'L1528'),
                      ("src/sgd/convert/data/strains/RedStar_JRIL00000000.gff", "src/sgd/convert/data/strains/RedStar_JRIL00000000_cds.fsa", 'RedStar'),
                      ("src/sgd/convert/data/strains/RM11-1A_JRIP00000000.gff", "src/sgd/convert/data/strains/RM11-1A_JRIP00000000_cds.fsa", 'RM11-1a'),
                      ("src/sgd/convert/data/strains/SEY6210_JRIW00000000.gff", "src/sgd/convert/data/strains/SEY6210_JRIW00000000_cds.fsa", 'SEY6210'),
                      ("src/sgd/convert/data/strains/SK1_JRIH00000000.gff", "src/sgd/convert/data/strains/SK1_JRIH00000000_cds.fsa", 'SK1'),
                      ("src/sgd/convert/data/strains/UWOPS05-217-3_JRIM00000000.gff", "src/sgd/convert/data/strains/UWOPS05-217-3_JRIM00000000_cds.fsa", 'UWOPSS'),
                      ("src/sgd/convert/data/strains/W303_JRIU00000000.gff", "src/sgd/convert/data/strains/W303_JRIU00000000_cds.fsa", 'W303'),
                      ("src/sgd/convert/data/strains/X2180-1A_JRIX00000000.gff", "src/sgd/convert/data/strains/X2180-1A_JRIX00000000_cds.fsa", 'X2180-1A'),
                      ("src/sgd/convert/data/strains/Y55_JRIF00000000.gff", "src/sgd/convert/data/strains/Y55_JRIF00000000_cds.fsa", 'Y55'),
                      ("src/sgd/convert/data/strains/YJM339_JRIE00000000.gff", "src/sgd/convert/data/strains/YJM339_JRIE00000000_cds.fsa", 'YJM339'),
                      ("src/sgd/convert/data/strains/YPH499_JRIO00000000.gff", "src/sgd/convert/data/strains/YPH499_JRIO00000000_cds.fsa", 'YPH499'),
                      ("src/sgd/convert/data/strains/YPS128_JRID00000000.gff", "src/sgd/convert/data/strains/YPS128_JRID00000000_cds.fsa", 'YPS128'),
                      ("src/sgd/convert/data/strains/YPS163_JRIC00000000.gff", "src/sgd/convert/data/strains/YPS163_JRIC00000000_cds.fsa", 'YPS163'),
                      ("src/sgd/convert/data/strains/YS9_JRIB00000000.gff", "src/sgd/convert/data/strains/YS9_JRIB00000000_cds.fsa", 'YS9'),

]

protein_sequence_files = [
    ("src/sgd/convert/data/strains/orf_trans_all.fasta", 'S288C'),
                      ('src/sgd/convert/data/strains/Sigma1278b-10560-6B_JRIQ00000000_pep.fsa', 'Sigma1278b'),
                      ("src/sgd/convert/data/strains/AWRI1631_ABSV01000000_pep.fsa.txt", 'AWRI1631'),
                      ("src/sgd/convert/data/strains/AWRI796_ADVS01000000_pep.fsa.txt", 'AWRI796'),
                      ('src/sgd/convert/data/strains/BC187_JRII00000000_pep.fsa', 'BC187'),
                      ('src/sgd/convert/data/strains/BY4741_JRIS00000000_pep.fsa', 'BY4741'),
                      ('src/sgd/convert/data/strains/BY4742_JRIR00000000_pep.fsa', 'BY4742'),
                      ("src/sgd/convert/data/strains/CBS7960_AEWL01000000_pep.fsa.txt", 'CBS7960'),
                      ('src/sgd/convert/data/strains/CEN.PK2-1Ca_JRIV01000000_pep.fsa', 'CENPK'),
                      ("src/sgd/convert/data/strains/CLIB215_AEWP01000000_pep.fsa.txt", 'CLIB215'),
                      #("src/sgd/convert/data/strains/CLIB324_AEWM01000000_pep.fsa.txt", 'CLIB324'),
                      #("src/sgd/convert/data/strains/CLIB382_AFDG01000000_pep.fsa.txt", 'CLIB382'),
                      ('src/sgd/convert/data/strains/D273-10B_JRIY00000000_pep.fsa', 'D273-10B'),
                      ('src/sgd/convert/data/strains/DBVPG6044_JRIG00000000_pep.fsa', 'DBVPG6044'),
                      ("src/sgd/convert/data/strains/EC1118_PRJEA37863_pep.fsa.txt", 'EC1118'),
                      ("src/sgd/convert/data/strains/EC9-8_AGSJ01000000_pep.fsa.txt", 'EC9-8'),
                      ('src/sgd/convert/data/strains/FL100_JRIT00000000_pep.fsa', 'FL100'),
                      ("src/sgd/convert/data/strains/FostersB_AEHH01000000_pep.fsa.txt", 'FostersB'),
                      ("src/sgd/convert/data/strains/FostersO_AEEZ01000000_pep.fsa.txt", 'FostersO'),
                      ('src/sgd/convert/data/strains/FY1679_JRIN00000000_pep.fsa', 'FY1679'),
                      ("src/sgd/convert/data/strains/JAY291_ACFL01000000_pep.fsa.txt", 'JAY291'),
                      ('src/sgd/convert/data/strains/JK9-3d_JRIZ00000000_pep.fsa', 'JK9-3d'),
                      ('src/sgd/convert/data/strains/K11_JRIJ00000000_pep.fsa', 'K11'),
                      ("src/sgd/convert/data/strains/Kyokai7_BABQ01000000_pep.fsa.txt", 'Kyokai7'),
                      ('src/sgd/convert/data/strains/L1528_JRIK00000000_pep.fsa', 'L1528'),
                      ("src/sgd/convert/data/strains/LalvinQA23_ADVV01000000_pep.fsa.txt", 'LalvinQA23'),
                      #("src/sgd/convert/data/strains/M22_ABPC01000000_pep.fsa.txt", 'M22'),
                      ("src/sgd/convert/data/strains/PW5_AFDC01000000_pep.fsa.txt", 'PW5'),
                      ('src/sgd/convert/data/strains/RedStar_JRIL00000000_pep.fsa', 'RedStar'),
                      ('src/sgd/convert/data/strains/RM11-1A_JRIP00000000_pep.fsa', 'RM11-1a'),
                      ('src/sgd/convert/data/strains/SEY6210_JRIW00000000_pep.fsa', 'SEY6210'),
                      ('src/sgd/convert/data/strains/SK1_JRIH00000000_pep.fsa', 'SK1'),
                      ("src/sgd/convert/data/strains/T7_AFDE01000000_pep.fsa.txt", 'T7'),
                      #("src/sgd/convert/data/strains/T73_AFDF01000000_pep.fsa.txt", 'T73'),
                      ("src/sgd/convert/data/strains/UC5_AFDD01000000_pep.fsa.txt", 'UC5'),
                      ('src/sgd/convert/data/strains/UWOPS05-217-3_JRIM00000000_pep.fsa', 'UWOPSS'),
                      ('src/sgd/convert/data/strains/W303_JRIU00000000_pep.fsa', 'W303'),
                      ("src/sgd/convert/data/strains/Vin13_ADXC01000000_pep.fsa.txt", 'VIN13'),
                      ("src/sgd/convert/data/strains/VL3_AEJS01000000_pep.fsa.txt", 'VL3'),
                      ('src/sgd/convert/data/strains/X2180-1A_JRIX00000000_pep.fsa', 'X2180-1A'),
                      #("src/sgd/convert/data/strains/Y10_AEWK01000000_pep.fsa.txt", 'Y10'),
                      ('src/sgd/convert/data/strains/Y55_JRIF00000000_pep.fsa', 'Y55'),
                      ("src/sgd/convert/data/strains/YJM269_AEWN01000000_pep.fsa.txt", 'YJM269'),
                      ('src/sgd/convert/data/strains/YJM339_JRIE00000000_pep.fsa', 'YJM339'),
                      ("src/sgd/convert/data/strains/YJM789_AAFW02000000_pep.fsa.txt", 'YJM789'),
                      ('src/sgd/convert/data/strains/YPH499_JRIO00000000_pep.fsa', 'YPH499'),
                      ('src/sgd/convert/data/strains/YPS128_JRID00000000_pep.fsa', 'YPS128'),
                      ('src/sgd/convert/data/strains/YPS163_JRIC00000000_pep.fsa', 'YPS163'),
                      ('src/sgd/convert/data/strains/YS9_JRIB00000000_pep.fsa', 'YS9'),
                      ("src/sgd/convert/data/strains/ZTW1_AMDD00000000_pep.fsa.txt", 'ZTW1')]




def get_dna_sequence_library(gff3_file, remove_spaces=False):
    id_to_sequence = {}
    on_sequence = False
    current_id = None
    current_sequence = []
    for line in gff3_file:
        line = line.replace("\r\n","").replace("\n", "")
        if not on_sequence and line.startswith('>'):
            on_sequence = True
        if line.startswith('>'):
            if current_id is not None:
                id_to_sequence[current_id] = ''.join(current_sequence)
            current_id = line[1:]
            if remove_spaces:
                current_id = current_id.split(' ')[0]
            current_sequence = []
        elif on_sequence:
            current_sequence.append(line)

    if current_id is not None:
        id_to_sequence[current_id] = ''.join(current_sequence)

    return id_to_sequence

def reverse_complement(residues):
    basecomplement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 't': 'a', 'a': 't', 'c': 'g', 'g': 'c', 'n': 'n',
                      'W': 'W', 'Y': 'R', 'R': 'Y', 'S': 'S', 'K':'M', 'M':'K', 'B':'V', 'D':'H', 'H':'D', 'V':'B', 'N':'N'}
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

def get_sequence(parent_id, start, end, strand, sequence_library):
    if parent_id in sequence_library:
        residues = sequence_library[parent_id][start-1:end]
        if strand == '-':
            residues = reverse_complement(residues)
        return residues
    else:
        print 'Parent not found: ' + parent_id
