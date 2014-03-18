from decimal import Decimal
import hashlib
import logging
import sys

from sqlalchemy.orm import joinedload

from src.sgd.convert import create_or_update, OutputCreator


__author__ = 'kpaskov'

sequence_files = [("data/strains/saccharomyces_cerevisiae_R64-1-1_20110208.gff", 'S288C'),
                      ("data/strains/CEN.PK113-7D_AEHG00000000.gff", 'CEN.PK'),
                      ("data/strains/W303_ALAV00000000.gff", 'W303'),
                      ("data/strains/AWRI1631_ABSV01000000.gff", 'AWRI1631'),
                      ("data/strains/AWRI796_ADVS01000000.gff", 'AWRI796'),
                      ("data/strains/BY4741_Toronto_2012.gff", 'BY4741'),
                      ("data/strains/BY4742_Toronto_2012.gff", 'BY4742'),
                      ("data/strains/CBS7960_AEWL01000000.gff", 'CBS7960'),
                      ("data/strains/CLIB215_AEWP01000000.gff", 'CLIB215'),
                      ("data/strains/CLIB324_AEWM01000000.gff", 'CLIB324'),
                      ("data/strains/CLIB382_AFDG01000000.gff", 'CLIB382'),
                      ("data/strains/EC1118_PRJEA37863.gff", 'EC1118'),
                      ("data/strains/EC9-8_AGSJ01000000.gff", 'EC9-8'),
                      ("data/strains/FL100_AEWO01000000.gff", 'FL100'),
                      ("data/strains/FostersB_AEHH01000000.gff", 'FostersB'),
                      ("data/strains/FostersO_AEEZ01000000.gff", 'FostersO'),
                      ("data/strains/JAY291_ACFL01000000.gff", 'JAY291'),
                      ("data/strains/Kyokai7_BABQ01000000.gff", 'Kyokai7'),
                      ("data/strains/LalvinQA23_ADVV01000000.gff", 'LalvinQA23'),
                      ("data/strains/M22_ABPC01000000.gff", 'M22'),
                      ("data/strains/PW5_AFDC01000000.gff", 'PW5'),
                      ("data/strains/RM11-1a_AAEG01000000.gff", 'RM11-1a'),
                      ("data/strains/Sigma1278b_ACVY01000000.gff", 'Sigma1278b'),
                      ("data/strains/T7_AFDE01000000.gff", 'T7'),
                      ("data/strains/T73_AFDF01000000.gff", 'T73'),
                      ("data/strains/UC5_AFDD01000000.gff", 'UC5'),
                      ("data/strains/Vin13_ADXC01000000.gff", 'VIN13'),
                      ("data/strains/VL3_AEJS01000000.gff", 'VL3'),
                      ("data/strains/Y10_AEWK01000000.gff", 'Y10'),
                      ("data/strains/YJM269_AEWN01000000.gff", 'YJM269'),
                      ("data/strains/YJM789_AAFW02000000.gff", 'YJM789'),
                      ("data/strains/YPS163_ABPD01000000.gff", 'YPS163'),
                      ("data/strains/ZTW1_AMDD00000000.gff", 'ZTW1')]

protein_sequence_files = [("data/strains/orf_trans_all_R64-1-1_20110203.fasta", 'S288C'),
                      ("data/strains/CEN.PK113-7D_AEHG00000000_pep.fsa.txt", 'CEN.PK'),
                      ("data/strains/W303_ALAV00000000_pep.fsa.txt", 'W303'),
                      ("data/strains/AWRI1631_ABSV01000000_pep.fsa.txt", 'AWRI1631'),
                      ("data/strains/AWRI796_ADVS01000000_pep.fsa.txt", 'AWRI796'),
                      ("data/strains/BY4741_Toronto_2012_pep.fsa.txt", 'BY4741'),
                      ("data/strains/BY4742_Toronto_2012_pep.fsa.txt", 'BY4742'),
                      ("data/strains/CBS7960_AEWL01000000_pep.fsa.txt", 'CBS7960'),
                      ("data/strains/CLIB215_AEWP01000000_pep.fsa.txt", 'CLIB215'),
                      ("data/strains/CLIB324_AEWM01000000_pep.fsa.txt", 'CLIB324'),
                      ("data/strains/CLIB382_AFDG01000000_pep.fsa.txt", 'CLIB382'),
                      ("data/strains/EC1118_PRJEA37863_pep.fsa.txt", 'EC1118'),
                      ("data/strains/EC9-8_AGSJ01000000_pep.fsa.txt", 'EC9-8'),
                      ("data/strains/FL100_AEWO01000000_pep.fsa.txt", 'FL100'),
                      ("data/strains/FostersB_AEHH01000000_pep.fsa.txt", 'FostersB'),
                      ("data/strains/FostersO_AEEZ01000000_pep.fsa.txt", 'FostersO'),
                      ("data/strains/JAY291_ACFL01000000_pep.fsa.txt", 'JAY291'),
                      ("data/strains/Kyokai7_BABQ01000000_pep.fsa.txt", 'Kyokai7'),
                      ("data/strains/LalvinQA23_ADVV01000000_pep.fsa.txt", 'LalvinQA23'),
                      ("data/strains/M22_ABPC01000000_pep.fsa.txt", 'M22'),
                      ("data/strains/PW5_AFDC01000000_pep.fsa.txt", 'PW5'),
                      ("data/strains/RM11-1a_AAEG01000000_pep.fsa.txt", 'RM11-1a'),
                      ("data/strains/Sigma1278b_ACVY01000000_pep.fsa.txt", 'Sigma1278b'),
                      ("data/strains/T7_AFDE01000000_pep.fsa.txt", 'T7'),
                      ("data/strains/T73_AFDF01000000_pep.fsa.txt", 'T73'),
                      ("data/strains/UC5_AFDD01000000_pep.fsa.txt", 'UC5'),
                      ("data/strains/Vin13_ADXC01000000_pep.fsa.txt", 'VIN13'),
                      ("data/strains/VL3_AEJS01000000_pep.fsa.txt", 'VL3'),
                      ("data/strains/Y10_AEWK01000000_pep.fsa.txt", 'Y10'),
                      ("data/strains/YJM269_AEWN01000000_pep.fsa.txt", 'YJM269'),
                      ("data/strains/YJM789_AAFW02000000_pep.fsa.txt", 'YJM789'),
                      ("data/strains/YPS163_ABPD01000000_pep.fsa.txt", 'YPS163'),
                      ("data/strains/ZTW1_AMDD00000000_pep.fsa.txt", 'ZTW1')]

coding_sequence_files = [("data/strains/orf_coding_all_R64-1-1_20110203.fasta", 'S288C'),
                      ("data/strains/CEN.PK113-7D_AEHG00000000_cds.fsa.txt", 'CEN.PK'),
                      ("data/strains/W303_ALAV00000000_cds.fsa.txt", 'W303'),
                      ("data/strains/AWRI1631_ABSV01000000_cds.fsa.txt", 'AWRI1631'),
                      ("data/strains/AWRI796_ADVS01000000_cds.fsa.txt", 'AWRI796'),
                      ("data/strains/BY4741_Toronto_2012_cds.fsa.txt", 'BY4741'),
                      ("data/strains/BY4742_Toronto_2012_cds.fsa.txt", 'BY4742'),
                      ("data/strains/CBS7960_AEWL01000000_cds.fsa.txt", 'CBS7960'),
                      ("data/strains/CLIB215_AEWP01000000_cds.fsa.txt", 'CLIB215'),
                      ("data/strains/CLIB324_AEWM01000000_cds.fsa.txt", 'CLIB324'),
                      ("data/strains/CLIB382_AFDG01000000_cds.fsa.txt", 'CLIB382'),
                      ("data/strains/EC1118_PRJEA37863_cds.fsa.txt", 'EC1118'),
                      ("data/strains/EC9-8_AGSJ01000000_cds.fsa.txt", 'EC9-8'),
                      ("data/strains/FL100_AEWO01000000_cds.fsa.txt", 'FL100'),
                      ("data/strains/FostersB_AEHH01000000_cds.fsa.txt", 'FostersB'),
                      ("data/strains/FostersO_AEEZ01000000_cds.fsa.txt", 'FostersO'),
                      ("data/strains/JAY291_ACFL01000000_cds.fsa.txt", 'JAY291'),
                      ("data/strains/Kyokai7_BABQ01000000_cds.fsa.txt", 'Kyokai7'),
                      ("data/strains/LalvinQA23_ADVV01000000_cds.fsa.txt", 'LalvinQA23'),
                      ("data/strains/M22_ABPC01000000_cds.fsa.txt", 'M22'),
                      ("data/strains/PW5_AFDC01000000_cds.fsa.txt", 'PW5'),
                      ("data/strains/RM11-1a_AAEG01000000_cds.fsa.txt", 'RM11-1a'),
                      ("data/strains/Sigma1278b_ACVY01000000_cds.fsa.txt", 'Sigma1278b'),
                      ("data/strains/T7_AFDE01000000_cds.fsa.txt", 'T7'),
                      ("data/strains/T73_AFDF01000000_cds.fsa.txt", 'T73'),
                      ("data/strains/UC5_AFDD01000000_cds.fsa.txt", 'UC5'),
                      ("data/strains/Vin13_ADXC01000000_cds.fsa.txt", 'VIN13'),
                      ("data/strains/VL3_AEJS01000000_cds.fsa.txt", 'VL3'),
                      ("data/strains/Y10_AEWK01000000_cds.fsa.txt", 'Y10'),
                      ("data/strains/YJM269_AEWN01000000_cds.fsa.txt", 'YJM269'),
                      ("data/strains/YJM789_AAFW02000000_cds.fsa.txt", 'YJM789'),
                      ("data/strains/YPS163_ABPD01000000_cds.fsa.txt", 'YPS163'),
                      ("data/strains/ZTW1_AMDD00000000_cds.fsa.txt", 'ZTW1')]

# --------------------- Convert DNA Sequence ---------------------
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
    from src.sgd.model.nex.sequence import Dnasequence
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

def create_coding_dna_sequence(id_to_sequence):
    from src.sgd.model.nex.sequence import Dnasequence
    return [Dnasequence(x) for x in id_to_sequence.values()]

def convert_strain_dna_sequence(filename, coding_filename, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
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

    f = open(coding_filename, 'r')
    sequence_library = get_sequence_library_fsa(f)
    f.close()

    #Convert old objects into new ones
    newly_created_objs = create_coding_dna_sequence(sequence_library)

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

def convert_dna_sequence(new_session_maker):
    from src.sgd.model.nex.sequence import Dnasequence

    new_session = None
    log = logging.getLogger('convert.sequence.sequence')
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

        for i in range(0, len(sequence_files)):
            filename, strain = sequence_files[i]
            coding_filename, _ = coding_sequence_files[i]
            convert_strain_dna_sequence(filename, coding_filename, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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

# --------------------- Convert DNA Sequence Evidence ---------------------
def get_info(data):
    info = {}
    for entry in data.split(';'):
        pieces = entry.split('=')
        if len(pieces) == 2:
            info[pieces[0]] = pieces[1]
    return info

def create_dna_evidence(row, strain, key_to_source, key_to_sequence, key_to_bioentity, sequence_library):
    from src.sgd.model.nex.evidence import GenomicDNAsequenceevidence
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
                    return [GenomicDNAsequenceevidence(source, strain, key_to_bioentity[bioentity_key], key_to_sequence[sequence_key], contig, start, end, strand, None, None)]
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
    from src.sgd.model.nex.evidence import GenomicDNAsequenceevidence
    from src.sgd.model.nex.evelements import Source, Strain
    from src.sgd.model.nex.sequence import Sequence
    from src.sgd.model.nex.bioentity import Bioentity

    new_session = None
    log = logging.getLogger('convert.sequence.evidence')
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
        current_objs = new_session.query(GenomicDNAsequenceevidence).all()
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

# --------------------- Convert Coding DNA Sequence Evidence ---------------------
def create_coding_evidence(strain, id_to_sequence, key_to_source, key_to_bioentity, key_to_sequence):
    from src.sgd.model.nex.evidence import CodingDNAsequenceevidence
    from src.sgd.model.nex.sequence import Dnasequence
    source = key_to_source['SGD']

    bioentity_name_to_new_sequence = dict([(key, Dnasequence(value)) for key, value in id_to_sequence.iteritems()])

    evidences = []

    for bioentity_name, sequence in id_to_sequence.iteritems():
        bioentity_key = (bioentity_name, 'LOCUS')
        bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]

        sequence_key = bioentity_name_to_new_sequence[bioentity_name].unique_key()
        sequence = None if sequence_key not in key_to_sequence else key_to_sequence[sequence_key]

        if bioentity is None:
            print "Bioentity not found: " + str(bioentity_key)
        if sequence is None:
            print "Sequence not found: " + str(sequence_key)

        evidences.append(CodingDNAsequenceevidence(source, strain, bioentity, sequence, None, None))
    return evidences

def convert_strain_coding_evidence(filename, strain, key_to_source, key_to_bioentity, key_to_sequence, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_sequence_library_fsa(f)
    f.close()

    f = open(filename, 'r')

    #Convert old objects into new ones
    newly_created_objs = create_coding_evidence(strain, sequence_library, key_to_source, key_to_bioentity, key_to_sequence)

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

def convert_coding_evidence(new_session_maker):
    from src.sgd.model.nex.evidence import CodingDNAsequenceevidence
    from src.sgd.model.nex.sequence import Dnasequence
    from src.sgd.model.nex.evelements import Source, Strain
    from src.sgd.model.nex.bioentity import Locus

    new_session = None
    log = logging.getLogger('convert.evidence.coding')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = []

        #Grab current objects
        current_objs = new_session.query(CodingDNAsequenceevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_sequence = dict([(x.unique_key(), x) for x in new_session.query(Dnasequence).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Locus).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in protein_sequence_files:
            strain = key_to_strain[strain.replace('.', '')]
            convert_strain_coding_evidence(filename, strain, key_to_source, key_to_bioentity, key_to_sequence, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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
    from src.sgd.model.nex.evidence import SequenceLabel
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
    from src.sgd.model.nex.evidence import Sequenceevidence, SequenceLabel
    from src.sgd.model.nex.evelements import Source, Strain
    from src.sgd.model.nex.sequence import Dnasequence
    from src.sgd.model.nex.bioentity import Bioentity

    new_session = None
    log = logging.getLogger('convert.sequence.sequencelabels')
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

# --------------------- Convert Protein Sequence ---------------------
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

def create_protein_sequence(id_to_sequence):
    from src.sgd.model.nex.sequence import Proteinsequence
    return [Proteinsequence(x) for x in id_to_sequence.values()]

def convert_strain_protein_sequence(filename, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_sequence_library_fsa(f)
    f.close()

    #Convert old objects into new ones
    newly_created_objs = create_protein_sequence(sequence_library)

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

def convert_protein_sequence(new_session_maker):
    from src.sgd.model.nex.sequence import Proteinsequence

    new_session = None
    log = logging.getLogger('convert.sequence.protein')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['n_term_seq', 'c_term_seq']

        #Grab current objects
        current_objs = new_session.query(Proteinsequence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in protein_sequence_files:
            convert_strain_protein_sequence(filename, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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

def update_sequence_measurements(old_session_maker, new_session_maker):
    from src.sgd.model.nex.sequence import Proteinsequence
    from src.sgd.model.bud.sequence import ProteinInfo, Sequence

    old_session = None
    new_session = None
    log = logging.getLogger('convert.sequence.protein_measurements')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        feature_id_to_residues = dict([(x.feature_id, x.residues) for x in old_session.query(Sequence).filter(Sequence.seq_type == 'protein').filter(Sequence.is_current == 'Y').all()])
        old_objs = old_session.query(ProteinInfo).options(joinedload(ProteinInfo.details)).all()

        for old_obj in old_objs:
            residues = feature_id_to_residues[old_obj.feature_id]
            format_name = str(hashlib.md5(residues).hexdigest())
            psequence = new_session.query(Proteinsequence).filter(Proteinsequence.format_name == format_name).first()

            if psequence is None:
                print 'Sequence not found: ' + str(old_obj.feature_id)
            else:
                if psequence.molecular_weight != old_obj.molecular_weight:
                    psequence.molecular_weight = old_obj.molecular_weight
                    output_creator.changed(hash, 'molecular_weight')

                if psequence.pi != old_obj.pi:
                    psequence.pi = old_obj.pi
                    output_creator.changed(hash, 'pi')

                if psequence.cai != old_obj.cai:
                    psequence.cai = old_obj.cai
                    output_creator.changed(hash, 'cai')

                if psequence.codon_bias != old_obj.codon_bias:
                    psequence.codon_bias = old_obj.codon_bias
                    output_creator.changed(hash, 'codon_bias')

                if psequence.fop_score != old_obj.fop_score:
                    psequence.fop_score = old_obj.fop_score
                    output_creator.changed(hash, 'fop_score')

                if psequence.gravy_score != old_obj.gravy_score:
                    psequence.gravy_score = old_obj.gravy_score
                    output_creator.changed(hash, 'gravy_score')

                if psequence.aromaticity_score != old_obj.aromaticity_score:
                    psequence.aromaticity_score = old_obj.aromaticity_score
                    output_creator.changed(hash, 'aromaticity_score')

                for detail in old_obj.details:
                    if detail.type == 'Aliphatic index':
                        if psequence.aliphatic_index != Decimal(detail.value):
                            psequence.aliphatic_index = Decimal(detail.value)
                            output_creator.changed(hash, 'aliphatic_index')

                    if detail.type == 'Hydrogen':
                        if psequence.hydrogen != int(detail.value):
                            psequence.hydrogen = int(detail.value)
                            output_creator.changed(hash, 'hydrogen')

                    if detail.type == 'Sulfur':
                        if psequence.sulfur != int(detail.value):
                            psequence.sulfur = int(detail.value)
                            output_creator.changed(hash, 'sulfur')

                    if detail.type == 'Nitrogen':
                        if psequence.nitrogen != int(detail.value):
                            psequence.nitrogen = int(detail.value)
                            output_creator.changed(hash, 'nitrogen')

                    if detail.type == 'Oxygen':
                        if psequence.oxygen != int(detail.value):
                            psequence.oxygen = int(detail.value)
                            output_creator.changed(hash, 'oxygen')

                    if detail.type == 'Carbon':
                        if psequence.carbon != int(detail.value):
                            psequence.carbon = int(detail.value)
                            output_creator.changed(hash, 'carbon')

                    if detail.type == 'yeast (in vivo)':
                        if psequence.yeast_half_life != detail.value:
                            psequence.yeast_half_life = detail.value
                            output_creator.changed(hash, 'yeast_half_life')

                    if detail.type == 'Escherichia coli (in vivo)':
                        if psequence.ecoli_half_life != detail.value:
                            psequence.ecoli_half_life = detail.value
                            output_creator.changed(hash, 'ecoli_half_life')

                    if detail.type == 'mammalian reticulocytes (in vitro)':
                        if psequence.mammal_half_life != detail.value:
                            psequence.mammal_half_life = detail.value
                            output_creator.changed(hash, 'mammal_half_life')

                    if detail.type == 'assuming NO Cys residues appear as half cystines':
                        if psequence.no_cys_ext_coeff != detail.value:
                            psequence.no_cys_ext_coeff = detail.value
                            output_creator.changed(hash, 'no_cys_ext_coeff')

                    if detail.type == 'assuming all Cys residues are reduced':
                        if psequence.all_cys_ext_coeff != detail.value:
                            psequence.all_cys_ext_coeff = detail.value
                            output_creator.changed(hash, 'all_cys_ext_coeff')

                    if detail.type == 'assuming ALL Cys residues appear as half cystines':
                        if psequence.all_half_cys_ext_coeff != detail.value:
                            psequence.all_half_cys_ext_coeff = detail.value
                            output_creator.changed(hash, 'all_half_cys_ext_coeff')

                    if detail.type == 'assuming all pairs of Cys residues form cystines':
                        if psequence.all_pairs_cys_ext_coeff != detail.value:
                            psequence.all_pairs_cys_ext_coeff = detail.value
                            output_creator.changed(hash, 'all_pairs_cys_ext_coeff')

                    if detail.type == 'Instability index (II)':
                        if psequence.instability_index != Decimal(detail.value):
                            psequence.instability_index = Decimal(detail.value)
                            output_creator.changed(hash, 'instability_index')

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()

# --------------------- Convert Protein Sequence Evidence ---------------------
def create_protein_evidence(strain, id_to_sequence, key_to_source, key_to_bioentity, key_to_sequence):
    from src.sgd.model.nex.evidence import Proteinsequenceevidence
    from src.sgd.model.nex.sequence import Proteinsequence
    source = key_to_source['SGD']

    bioentity_name_to_new_sequence = dict([(key, Proteinsequence(value)) for key, value in id_to_sequence.iteritems()])

    proteinevidences = []

    for bioentity_name, sequence in id_to_sequence.iteritems():
        bioentity_key = (bioentity_name + 'P', 'PROTEIN')
        bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]

        sequence_key = bioentity_name_to_new_sequence[bioentity_name].unique_key()
        sequence = None if sequence_key not in key_to_sequence else key_to_sequence[sequence_key]

        if bioentity is None:
            print "Bioentity not found: " + str(bioentity_key)
        if sequence is None:
            print "Sequence not found: " + str(sequence_key)

        proteinevidences.append(Proteinsequenceevidence(source, strain, bioentity, sequence, None, None))
    return proteinevidences

def convert_strain_protein_evidence(filename, strain, key_to_source, key_to_bioentity, key_to_sequence, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_sequence_library_fsa(f)
    f.close()

    f = open(filename, 'r')

    #Convert old objects into new ones
    newly_created_objs = create_protein_evidence(strain, sequence_library, key_to_source, key_to_bioentity, key_to_sequence)

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

def convert_protein_evidence(new_session_maker):
    from src.sgd.model.nex.evidence import Proteinsequenceevidence
    from src.sgd.model.nex.sequence import Proteinsequence
    from src.sgd.model.nex.evelements import Source, Strain
    from src.sgd.model.nex.bioentity import Protein

    new_session = None
    log = logging.getLogger('convert.evidence.protein')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = []

        #Grab current objects
        current_objs = new_session.query(Proteinsequenceevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Grab cached dictionaries
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_sequence = dict([(x.unique_key(), x) for x in new_session.query(Proteinsequence).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Protein).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in protein_sequence_files:
            strain = key_to_strain[strain.replace('.', '')]
            convert_strain_protein_evidence(filename, strain, key_to_source, key_to_bioentity, key_to_sequence, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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

# --------------------- Convert Contig Sequence ---------------------
def create_contig(sequence_library, strain):
    from src.sgd.model.nex.sequence import Contig
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
    from src.sgd.model.nex.sequence import Contig
    from src.sgd.model.nex.evelements import Strain

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

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_contig(filename, key_to_strain[strain.replace('.', '')], values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

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
    #from nex.sequence import Contig
    #convert_disambigs(new_session_maker, Contig, ['id', 'format_name'], 'SEQUENCE', 'CONTIG', 'convert.contig.disambigs', 1000)

    #convert_dna_sequence(new_session_maker)
    #convert_dna_evidence(new_session_maker)
    convert_coding_evidence(new_session_maker)
    #convert_dna_sequence_label(new_session_maker)

    #convert_protein_sequence(new_session_maker)
    #update_sequence_measurements(old_session_maker, new_session_maker)
    #convert_protein_evidence(new_session_maker)

    #class SeqLab():
    #    def __init__(self, relative_start, relative_end, class_type):
    #        self.relative_end = relative_end
    #        self.relative_start = relative_start
    #        self.class_type = class_type


    #labels = [SeqLab(1, 10, "CDS"), SeqLab(11, 319, "intron"), SeqLab(320, 1437, "CDS")]
    #residues = "ATGGATTCTGGTATGTTCTAGCGCTTGCACCATCCCATTTAACTGTAAGAAGAATTGCACGGTCCCAATTGCTCGAGAGATTTCTCTTTTACCTTTTTTTACTATTTTTCACTCTCCCATAACCTCCTATATTGACTGATCTGTAATAACCACGATATTATTGGAATAAATAGGGGCTTGAAATTTGGAAAAAAAAAAAAAACTGAAATATTTTCGTGATAAGTGATAGTGATATTCTTCTTTTATTTGCTACTGTTACTAAGTCTCATGTACTAACATCGATTGCTTCATTCTTTTTGTTGCTATATTATATGTTTAGAGGTTGCTGCTTTGGTTATTGATAACGGTTCTGGTATGTGTAAAGCCGGTTTTGCCGGTGACGACGCTCCTCGTGCTGTCTTCCCATCTATCGTCGGTAGACCAAGACACCAAGGTATCATGGTCGGTATGGGTCAAAAAGACTCCTACGTTGGTGATGAAGCTCAATCCAAGAGAGGTATCTTGACTTTACGTTACCCAATTGAACACGGTATTGTCACCAACTGGGACGATATGGAAAAGATCTGGCATCATACCTTCTACAACGAATTGAGAGTTGCCCCAGAAGAACACCCTGTTCTTTTGACTGAAGCTCCAATGAACCCTAAATCAAACAGAGAAAAGATGACTCAAATTATGTTTGAAACTTTCAACGTTCCAGCCTTCTACGTTTCCATCCAAGCCGTTTTGTCCTTGTACTCTTCCGGTAGAACTACTGGTATTGTTTTGGATTCCGGTGATGGTGTTACTCACGTCGTTCCAATTTACGCTGGTTTCTCTCTACCTCACGCCATTTTGAGAATCGATTTGGCCGGTAGAGATTTGACTGACTACTTGATGAAGATCTTGAGTGAACGTGGTTACTCTTTCTCCACCACTGCTGAAAGAGAAATTGTCCGTGACATCAAGGAAAAACTATGTTACGTCGCCTTGGACTTCGAACAAGAAATGCAAACCGCTGCTCAATCTTCTTCAATTGAAAAATCCTACGAACTTCCAGATGGTCAAGTCATCACTATTGGTAACGAAAGATTCAGAGCCCCAGAAGCTTTGTTCCATCCTTCTGTTTTGGGTTTGGAATCTGCCGGTATTGACCAAACTACTTACAACTCCATCATGAAGTGTGATGTCGATGTCCGTAAGGAATTATACGGTAACATCGTTATGTCCGGTGGTACCACCATGTTCCCAGGTATTGCCGAAAGAATGCAAAAGGAAATCACCGCTTTGGCTCCATCTTCCATGAAGGTCAAGATCATTGCTCCTCCAGAAAGAAAGTACTCCGTCTGGATTGGTGGTTCTATCTTGGCTTCTTTGACTACCTTCCAACAAATGTGGATCTCAAAACAAGAATACGACGAAAGTGGTCCATCTATCGTTCACCACAAGTGTTTCTAA"
    #print translate(residues, labels)