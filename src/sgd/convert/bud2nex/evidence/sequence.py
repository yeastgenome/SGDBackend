from decimal import Decimal
import logging
import sys

from sqlalchemy.orm import joinedload

from src.sgd.convert import create_or_update, OutputCreator


__author__ = 'kpaskov'

sequence_files = [("src/sgd/convert/data/strains/saccharomyces_cerevisiae_R64-1-1_20110208.gff", 'S288C'),
                      ("src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000.gff", 'CENPK'),
                      ("src/sgd/convert/data/strains/W303_ALAV00000000.gff", 'W303'),
                      ("src/sgd/convert/data/strains/AWRI1631_ABSV01000000.gff", 'AWRI1631'),
                      ("src/sgd/convert/data/strains/AWRI796_ADVS01000000.gff", 'AWRI796'),
                      ("src/sgd/convert/data/strains/BY4741_Toronto_2012.gff", 'BY4741'),
                      ("src/sgd/convert/data/strains/BY4742_Toronto_2012.gff", 'BY4742'),
                      ("src/sgd/convert/data/strains/CBS7960_AEWL01000000.gff", 'CBS7960'),
                      ("src/sgd/convert/data/strains/CLIB215_AEWP01000000.gff", 'CLIB215'),
                      ("src/sgd/convert/data/strains/CLIB324_AEWM01000000.gff", 'CLIB324'),
                      ("src/sgd/convert/data/strains/CLIB382_AFDG01000000.gff", 'CLIB382'),
                      ("src/sgd/convert/data/strains/EC1118_PRJEA37863.gff", 'EC1118'),
                      ("src/sgd/convert/data/strains/EC9-8_AGSJ01000000.gff", 'EC9-8'),
                      ("src/sgd/convert/data/strains/FL100_AEWO01000000.gff", 'FL100'),
                      ("src/sgd/convert/data/strains/FostersB_AEHH01000000.gff", 'FostersB'),
                      ("src/sgd/convert/data/strains/FostersO_AEEZ01000000.gff", 'FostersO'),
                      ("src/sgd/convert/data/strains/JAY291_ACFL01000000.gff", 'JAY291'),
                      ("src/sgd/convert/data/strains/Kyokai7_BABQ01000000.gff", 'Kyokai7'),
                      ("src/sgd/convert/data/strains/LalvinQA23_ADVV01000000.gff", 'LalvinQA23'),
                      ("src/sgd/convert/data/strains/M22_ABPC01000000.gff", 'M22'),
                      ("src/sgd/convert/data/strains/PW5_AFDC01000000.gff", 'PW5'),
                      ("src/sgd/convert/data/strains/RM11-1a_AAEG01000000.gff", 'RM11-1a'),
                      ("src/sgd/convert/data/strains/Sigma1278b_ACVY01000000.gff", 'Sigma1278b'),
                      ("src/sgd/convert/data/strains/T7_AFDE01000000.gff", 'T7'),
                      ("src/sgd/convert/data/strains/T73_AFDF01000000.gff", 'T73'),
                      ("src/sgd/convert/data/strains/UC5_AFDD01000000.gff", 'UC5'),
                      ("src/sgd/convert/data/strains/Vin13_ADXC01000000.gff", 'VIN13'),
                      ("src/sgd/convert/data/strains/VL3_AEJS01000000.gff", 'VL3'),
                      ("src/sgd/convert/data/strains/Y10_AEWK01000000.gff", 'Y10'),
                      ("src/sgd/convert/data/strains/YJM269_AEWN01000000.gff", 'YJM269'),
                      ("src/sgd/convert/data/strains/YJM789_AAFW02000000.gff", 'YJM789'),
                      ("src/sgd/convert/data/strains/YPS163_ABPD01000000.gff", 'YPS163'),
                      ("src/sgd/convert/data/strains/ZTW1_AMDD00000000.gff", 'ZTW1')]

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

coding_sequence_files = [("src/sgd/convert/data/strains/orf_coding_all_R64-1-1_20110203.fasta", 'S288C'),
                      ("src/sgd/convert/data/strains/CEN.PK113-7D_AEHG00000000_cds.fsa.txt", 'CENPK'),
                      ("src/sgd/convert/data/strains/W303_ALAV00000000_cds.fsa.txt", 'W303'),
                      ("src/sgd/convert/data/strains/AWRI1631_ABSV01000000_cds.fsa.txt", 'AWRI1631'),
                      ("src/sgd/convert/data/strains/AWRI796_ADVS01000000_cds.fsa.txt", 'AWRI796'),
                      ("src/sgd/convert/data/strains/BY4741_Toronto_2012_cds.fsa.txt", 'BY4741'),
                      ("src/sgd/convert/data/strains/BY4742_Toronto_2012_cds.fsa.txt", 'BY4742'),
                      ("src/sgd/convert/data/strains/CBS7960_AEWL01000000_cds.fsa.txt", 'CBS7960'),
                      ("src/sgd/convert/data/strains/CLIB215_AEWP01000000_cds.fsa.txt", 'CLIB215'),
                      ("src/sgd/convert/data/strains/CLIB324_AEWM01000000_cds.fsa.txt", 'CLIB324'),
                      ("src/sgd/convert/data/strains/CLIB382_AFDG01000000_cds.fsa.txt", 'CLIB382'),
                      ("src/sgd/convert/data/strains/EC1118_PRJEA37863_cds.fsa.txt", 'EC1118'),
                      ("src/sgd/convert/data/strains/EC9-8_AGSJ01000000_cds.fsa.txt", 'EC9-8'),
                      ("src/sgd/convert/data/strains/FL100_AEWO01000000_cds.fsa.txt", 'FL100'),
                      ("src/sgd/convert/data/strains/FostersB_AEHH01000000_cds.fsa.txt", 'FostersB'),
                      ("src/sgd/convert/data/strains/FostersO_AEEZ01000000_cds.fsa.txt", 'FostersO'),
                      ("src/sgd/convert/data/strains/JAY291_ACFL01000000_cds.fsa.txt", 'JAY291'),
                      ("src/sgd/convert/data/strains/Kyokai7_BABQ01000000_cds.fsa.txt", 'Kyokai7'),
                      ("src/sgd/convert/data/strains/LalvinQA23_ADVV01000000_cds.fsa.txt", 'LalvinQA23'),
                      ("src/sgd/convert/data/strains/M22_ABPC01000000_cds.fsa.txt", 'M22'),
                      ("src/sgd/convert/data/strains/PW5_AFDC01000000_cds.fsa.txt", 'PW5'),
                      ("src/sgd/convert/data/strains/RM11-1a_AAEG01000000_cds.fsa.txt", 'RM11-1a'),
                      ("src/sgd/convert/data/strains/Sigma1278b_ACVY01000000_cds.fsa.txt", 'Sigma1278b'),
                      ("src/sgd/convert/data/strains/T7_AFDE01000000_cds.fsa.txt", 'T7'),
                      ("src/sgd/convert/data/strains/T73_AFDF01000000_cds.fsa.txt", 'T73'),
                      ("src/sgd/convert/data/strains/UC5_AFDD01000000_cds.fsa.txt", 'UC5'),
                      ("src/sgd/convert/data/strains/Vin13_ADXC01000000_cds.fsa.txt", 'VIN13'),
                      ("src/sgd/convert/data/strains/VL3_AEJS01000000_cds.fsa.txt", 'VL3'),
                      ("src/sgd/convert/data/strains/Y10_AEWK01000000_cds.fsa.txt", 'Y10'),
                      ("src/sgd/convert/data/strains/YJM269_AEWN01000000_cds.fsa.txt", 'YJM269'),
                      ("src/sgd/convert/data/strains/YJM789_AAFW02000000_cds.fsa.txt", 'YJM789'),
                      ("src/sgd/convert/data/strains/YPS163_ABPD01000000_cds.fsa.txt", 'YPS163'),
                      ("src/sgd/convert/data/strains/ZTW1_AMDD00000000_cds.fsa.txt", 'ZTW1')]

sequence_class_types = {'gene', 'ARS', 'tRNA', 'ncRNA', 'mRNA', 'snoRNA', 'rRNA'}

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

# --------------------- Convert DNA Sequence Evidence ---------------------
def get_info(data):
    info = {}
    for entry in data.split(';'):
        pieces = entry.split('=')
        if len(pieces) == 2:
            info[pieces[0]] = pieces[1]
    return info

def create_dna_evidence(row, strain, key_to_source, key_to_bioentity, key_to_bioitem, sequence_library):
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    source = key_to_source['SGD']
    pieces = row.split('\t')
    if len(pieces) == 9:
        parent_id = pieces[0]
        start = int(pieces[3])
        end = int(pieces[4])
        strand = pieces[6]
        info = get_info(pieces[8])
        class_type = pieces[2]
        residues = get_sequence(row, sequence_library)

        if 'Name' in info and class_type in sequence_class_types:
            bioentity_key = (info['Name'], 'LOCUS')
            contig = key_to_bioitem[(strain.format_name + '_' + parent_id, 'CONTIG')]
            if bioentity_key in key_to_bioentity:
                return [DNAsequenceevidence(source, strain, key_to_bioentity[bioentity_key], 'GENOMIC', residues, contig, start, end, strand, None, None)]
    return []

def convert_strain_dna_evidence(filename, strain, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids, key_to_source, key_to_bioentity, key_to_bioitem):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    f = open(filename, 'r')
    for old_obj in f:
        #Convert old objects into new ones
        newly_created_objs = create_dna_evidence(old_obj, strain, key_to_source, key_to_bioentity, key_to_bioitem, sequence_library)

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
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Contig

    new_session = None
    log = logging.getLogger('convert.evidence.genomic')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['start', 'end', 'strand', 'contig_id']

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Locus).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in new_session.query(Contig).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        #Grab current objects
        current_objs = new_session.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_dna_evidence(filename, key_to_strain[strain], values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids, key_to_source, key_to_bioentity, key_to_bioitem)

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

# --------------------- Convert Coding DNA Sequence Evidence ---------------------
def create_coding_evidence(strain, id_to_sequence, key_to_source, key_to_bioentity):
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    source = key_to_source['SGD']

    evidences = []

    for bioentity_name, sequence in id_to_sequence.iteritems():
        bioentity_key = (bioentity_name, 'LOCUS')
        bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]

        if bioentity is None:
            print "Bioentity not found: " + str(bioentity_key)
        else:
            evidences.append(DNAsequenceevidence(source, strain, bioentity, 'CODING', sequence, None, None, None, None, None, None))
    return evidences

def convert_strain_coding_evidence(filename, strain, key_to_source, key_to_bioentity, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_sequence_library_fsa(f)
    f.close()

    #Convert old objects into new ones
    newly_created_objs = create_coding_evidence(strain, sequence_library, key_to_source, key_to_bioentity)

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

def convert_coding_evidence(new_session_maker):
    from src.sgd.model.nex.evidence import DNAsequenceevidence
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Locus

    new_session = None
    log = logging.getLogger('convert.evidence.coding')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = []

        #Grab current objects
        current_objs = new_session.query(DNAsequenceevidence).filter_by(dna_type='CODING').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Locus).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in protein_sequence_files:
            strain = key_to_strain[strain.replace('.', '')]
            convert_strain_coding_evidence(filename, strain, key_to_source, key_to_bioentity, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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

# --------------------- DNA Convert Sequence Label ---------------------
def create_dna_sequence_label(row, parent_id_to_evidence):
    from src.sgd.model.nex.evidence import DNAsequencetag
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
                return [DNAsequencetag(evidence, class_type, relative_start, relative_end, chromosomal_start, chromosomal_end, phase, None, None)]
    return []

def get_parent_id_to_dna_evidence(f, strain, key_to_source, key_to_bioentity, sequence_library, key_to_evidence):
    parent_id_to_evidence = {}
    for line in f:
        pieces = line.split('\t')
        if len(pieces) == 9:
            info = get_info(pieces[8])
            evidence = create_dna_evidence(line, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library)
            if len(evidence) == 1 and 'ID' in info:
                parent_id_to_evidence[info['ID']] = key_to_evidence[evidence[0].unique_key()]
    return parent_id_to_evidence

def convert_strain_dna_sequence_label(filename, strain, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids, key_to_source, key_to_bioentity, key_to_evidence):
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    f = open(filename, 'r')
    parent_id_to_evidence = get_parent_id_to_dna_evidence(f, strain, key_to_source, key_to_bioentity, sequence_library, key_to_evidence)
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
    from src.sgd.model.nex.evidence import DNAsequenceevidence, DNAsequencetag
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Bioentity

    new_session = None
    log = logging.getLogger('convert.sequence.sequencetags')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['relative_start', 'relative_end', 'phase']

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
        key_to_evidence = dict([(x.unique_key(), x) for x in new_session.query(DNAsequenceevidence).all()])

        #Grab current objects
        current_objs = new_session.query(DNAsequencetag).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_dna_sequence_label(filename, key_to_strain[strain],
                                      values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids,
                                      key_to_source, key_to_bioentity, key_to_evidence)

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

# --------------------- Convert Protein Sequence Evidence ---------------------
def create_protein_evidence(strain, id_to_sequence, key_to_source, key_to_bioentity, bioentity_id_to_protein_info):
    from src.sgd.model.nex.evidence import Proteinsequenceevidence
    source = key_to_source['SGD']

    proteinevidences = []

    for bioentity_name, sequence in id_to_sequence.iteritems():
        bioentity_key = (bioentity_name + 'P', 'PROTEIN')
        bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]

        if bioentity is None:
            print "Bioentity not found: " + str(bioentity_key)
        else:
            evidence = Proteinsequenceevidence(source, strain, bioentity, 'PROTEIN', sequence, None, None)
            if strain.id == 1 and bioentity.id in bioentity_id_to_protein_info:
                protein_info = bioentity_id_to_protein_info[bioentity.id]
                evidence.molecular_weight = protein_info.molecular_weight
                evidence.pi = protein_info.pi
                evidence.cai = protein_info.cai
                evidence.codon_bias = protein_info.codon_bias
                evidence.fop_score = protein_info.fop_score
                evidence.gravy_score = protein_info.gravy_score
                evidence.aromaticity_score = protein_info.aromaticity_score

                for detail in protein_info.details:
                    if detail.type == 'Aliphatic index':
                        evidence.aliphatic_index = Decimal(detail.value)
                    if detail.type == 'Hydrogen':
                        evidence.hydrogen = int(detail.value)
                    if detail.type == 'Sulfur':
                        evidence.sulfur = int(detail.value)
                    if detail.type == 'Nitrogen':
                        evidence.nitrogen = int(detail.value)
                    if detail.type == 'Oxygen':
                        evidence.oxygen = int(detail.value)
                    if detail.type == 'Carbon':
                        evidence.carbon = int(detail.value)
                    if detail.type == 'yeast (in vivo)':
                        evidence.yeast_half_life = detail.value
                    if detail.type == 'Escherichia coli (in vivo)':
                        evidence.ecoli_half_life = detail.value
                    if detail.type == 'mammalian reticulocytes (in vitro)':
                        evidence.mammal_half_life = detail.value
                    if detail.type == 'assuming NO Cys residues appear as half cystines':
                        evidence.no_cys_ext_coeff = detail.value
                    if detail.type == 'assuming all Cys residues are reduced':
                        evidence.all_cys_ext_coeff = detail.value
                    if detail.type == 'assuming ALL Cys residues appear as half cystines':
                        evidence.all_half_cys_ext_coeff = detail.value
                    if detail.type == 'assuming all pairs of Cys residues form cystines':
                        evidence.all_pairs_cys_ext_coeff = detail.value
                    if detail.type == 'Instability index (II)':
                        evidence.instability_index = Decimal(detail.value)
            proteinevidences.append(evidence)
    return proteinevidences

def convert_strain_protein_evidence(filename, strain, key_to_source, key_to_bioentity, bioentity_id_to_protein_info, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_sequence_library_fsa(f)
    f.close()

    #Convert old objects into new ones
    newly_created_objs = create_protein_evidence(strain, sequence_library, key_to_source, key_to_bioentity, bioentity_id_to_protein_info)

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

def convert_protein_evidence(old_session_maker, new_session_maker):
    from src.sgd.model.nex.evidence import Proteinsequenceevidence
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Protein
    from src.sgd.model.bud.sequence import ProteinInfo

    new_session = None
    old_session = None
    log = logging.getLogger('convert.evidence.protein')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Values to check
        values_to_check = ['residues', 'strain_id', 'reference_id' 'source_id', 'experiment_id', 'bioentity_id',
                           'protein_type', 'molecular_weight', 'pi', 'cai', 'n_term_seq', 'c_term_seq', 'codon_bias', 'fop_score', 'gravy_score',
                           'aromaticity_score', 'aliphatic_index', 'instability_index', 'ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly',
                           'his', 'ile', 'leu', 'lys', 'met', 'phe', 'pro', 'thr', 'ser', 'trp', 'tyr', 'val', 'hydrogen', 'sulfur', 'nitrogen', 'oxygen', 'carbon', 'yeast_half_life',
                           'ecoli_half_life', 'mammal_half_life', 'no_cys_ext_coeff', 'all_cys_ext_coeff', 'all_half_cys_ext_coeff', 'all_pairs_cys_ext_coeff']

        #Grab current objects
        current_objs = new_session.query(Proteinsequenceevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Protein).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        bioentity_id_to_protein_info = dict([(x.feature_id, x) for x in old_session.query(ProteinInfo).options(joinedload(ProteinInfo.details)).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in protein_sequence_files:
            strain = key_to_strain[strain.replace('.', '')]
            convert_strain_protein_evidence(filename, strain, key_to_source, key_to_bioentity, bioentity_id_to_protein_info, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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
        old_session.close()

# --------------------- Convert Contig Sequence ---------------------
def create_contig(sequence_library, strain, source):
    from src.sgd.model.nex.bioitem import Contig
    return [Contig(x, source, y, strain) for x, y in sequence_library.iteritems()]

def convert_strain_contig(filename, strain, key_to_source, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    source = key_to_source['SGD']
    newly_created_objs = create_contig(sequence_library, strain, source)

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
    from src.sgd.model.nex.bioitem import Contig
    from src.sgd.model.nex.misc import Strain, Source

    new_session = None
    log = logging.getLogger('convert.sequence.contig')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['display_name', 'residues', 'link']

        #Grab current objects
        current_objs = new_session.query(Contig).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_contig(filename, key_to_strain[strain.replace('.', '')], key_to_source, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

        #Delete untouched objs
        for untouched_obj_id in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):

    #convert_contig(new_session_maker)
    #from src.sgd.model.nex.bioitem import Contig
    #convert_disambigs(new_session_maker, Contig, ['id', 'format_name'], 'BIOITEM', 'CONTIG', 'convert.contig.disambigs', 1000)

    convert_dna_evidence(new_session_maker)
    convert_coding_evidence(new_session_maker)
    #convert_dna_sequence_label(new_session_maker)

    convert_protein_evidence(old_session_maker, new_session_maker)
