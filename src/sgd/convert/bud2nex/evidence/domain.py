import logging
import sys

from sqlalchemy.orm import joinedload
from mpmath import ceil

from src.sgd.convert import OutputCreator, create_format_name, break_up_file, create_or_update


__author__ = 'kpaskov'

# --------------------- Convert Domain Evidence ---------------------
def create_domain_evidence(row, key_to_bioentity, key_to_domain, key_to_strain, key_to_source):
    from src.sgd.model.nex.evidence import Domainevidence
    
    bioent_format_name = row[1].strip()
    source_name = row[13].strip()
    domain_format_name = create_format_name(row[3].strip())
    start = row[10].strip()
    end = row[11].strip()
    evalue = row[12].strip()
    status = None
    date_of_run = None
    
    bioent_key = (bioent_format_name, 'LOCUS')
    if bioent_key not in key_to_bioentity:
        print 'Locus not found: ' + str(bioent_key)
        return []
    locus = key_to_bioentity[bioent_key]
    
    if source_name == 'HMMSmart':
        source_name = 'SMART'
    if source_name == 'HMMPanther':
        source_name = 'PANTHER'
    if source_name == 'FPrintScan':
        source_name = 'PRINTS'
    if source_name == 'HMMPfam':
        source_name = 'Pfam'
    if source_name == 'PatternScan' or source_name == 'ProfileScan':
        source_name = 'PROSITE'
    if source_name == 'BlastProDom':
        source_name = 'ProDom'
    if source_name == 'HMMTigr':
        source_name = 'TIGRFAMs'
    if source_name == 'HMMPIR':
        source_name = 'PIR_superfamily'
    if source_name == 'superfamily':
        source_name = 'SUPERFAMILY'
    if source_name == 'Seg' or source_name == 'Coil':
        source_name = '-'
    
    domain_key = (domain_format_name, 'DOMAIN')
    domain = None if domain_key not in key_to_domain else key_to_domain[domain_key]
    strain = key_to_strain['S288C']
    source = None if source_name not in key_to_source else key_to_source[source_name]
        
    domain_evidence = Domainevidence(source, None, strain, None, 
                                     int(start), int(end), evalue, status, date_of_run, locus, domain, None, None)
    return [domain_evidence]

def create_domain_evidence_from_tf_file(row, key_to_bioentity, key_to_domain, pubmed_id_to_reference, key_to_strain, key_to_source, locus_id_to_length):
    from src.sgd.model.nex.evidence import Domainevidence
    
    bioent_format_name = row[2].strip()
    source_name = 'JASPAR'
    db_identifier = row[0]
    start = 1
    evalue = None
    status = 'T'
    date_of_run = None
    pubmed_id = int(row[6].strip())
    
    bioent_key = (bioent_format_name, 'LOCUS')
    locus = None if bioent_key not in key_to_bioentity else key_to_bioentity[bioent_key]
    if protein is None:
        print bioent_key
        return []
    end = locus_id_to_length[locus.id]
    
    domain_key = (db_identifier, 'DOMAIN')
    domain = None if domain_key not in key_to_domain else key_to_domain[domain_key]
    strain = key_to_strain['S288C']
    source = None if source_name not in key_to_source else key_to_source[source_name]
    reference = None if pubmed_id not in pubmed_id_to_reference else pubmed_id_to_reference[pubmed_id]
    
    domain_evidence = Domainevidence(source, reference, strain, None, 
                                     start, end, evalue, status, date_of_run, locus, domain, None, None)
    return [domain_evidence]

def create_domain_evidence_from_protein_info(protein_detail, id_to_bioentity, key_to_bioentity, key_to_domain, key_to_source, key_to_strain):
    from src.sgd.model.nex.evidence import Domainevidence

    strain = key_to_strain['S288C']

    locus = id_to_bioentity[protein_detail.info.feature_id]

    if protein_detail.type == 'transmembrane domain':
        domain_key = ('predicted_transmembrane_domain', 'DOMAIN')
        source = key_to_source['TMHMM']
    elif protein_detail.type == 'signal peptide':
        domain_key = ('predicted_signal_peptide', 'DOMAIN')
        source = key_to_source['SignalP']
    else:
        #print 'Type not handled: ' + protein_detail.type
        return []

    domain = None if domain_key is None or domain_key not in key_to_domain else key_to_domain[domain_key]
    if domain is None:
        print 'Domain not found: ' + str(domain_key)
    else:
        if protein_detail.min_coord is None or protein_detail.max_coord is None:
            print 'Min or max coord is none.'
        else:
            domain_evidence = Domainevidence(source, None, strain, None,
                protein_detail.min_coord, protein_detail.max_coord, None, None, None, locus, domain,
                protein_detail.date_created, protein_detail.created_by)
            return [domain_evidence]

    return []

def convert_domain_evidence(old_session_maker, new_session_maker):
    from src.sgd.model.nex.evidence import Domainevidence, Proteinsequenceevidence
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.bioitem import Domain
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.bud.sequence import ProteinDetail as OldProteinDetail

    old_session = None
    new_session = None
    log = logging.getLogger('convert.protein_domain.evidence')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['reference_id', 'strain_id', 'source_id',
                           'start', 'end', 'evalue', 'status', 'date_of_run', 'bioentity_id', 'bioitem_id']
        
        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        id_to_bioentity = dict([(x.id, x) for x in key_to_bioentity.values()])
        print 'Bioentities'
        key_to_domain = dict([(x.unique_key(), x) for x in new_session.query(Domain).all()])
        print 'Domains'
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        print 'Ready'

        already_seen_obj = set()

        current_objs = new_session.query(Domainevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        print 'Evidence'

        untouched_obj_ids = set(id_to_current_obj.keys())

        #Grab old objects
        data = break_up_file('src/sgd/convert/data/yeastmine_protein_domains.tsv')

        num_chunks = ceil(1.0*len(data)/1000)

        for i in range(0, num_chunks):
                        
            old_objs = data[i*1000:(i+1)*1000]
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_domain_evidence(old_obj, key_to_bioentity, key_to_domain, key_to_strain, key_to_source)
                    
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    if obj_key not in already_seen_obj:
                        obj_id = newly_created_obj.id
                        current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                        current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen_obj.add(obj_key)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()

        #Grab protein_details
        old_session = old_session_maker()
        old_objs = old_session.query(OldProteinDetail).options(joinedload('info')).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_evidence_from_protein_info(old_obj, id_to_bioentity, key_to_bioentity, key_to_domain, key_to_source, key_to_strain)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen_obj:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                else:
                    print unique_key
                already_seen_obj.add(unique_key)

        output_creator.finished("1/2")
        new_session.commit()
            
        #Grab JASPAR evidence from file
        old_objs = break_up_file('src/sgd/convert/data/TF_family_class_accession04302013.txt')

        pubmed_ids = set([int(row[6].strip()) for row in old_objs])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in new_session.query(Reference).filter(Reference.pubmed_id.in_(pubmed_ids)).all()])

        protein_id_to_length = dict([(x.bioentity_id, x.residues.length) for x in new_session.query(Proteinsequenceevidence).filter(Proteinsequenceevidence.source_id == 1).all()])

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_evidence_from_tf_file(old_obj, key_to_bioentity, key_to_domain, pubmed_id_to_reference, key_to_strain, key_to_source, protein_id_to_length)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen_obj:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                else:
                    print unique_key
                already_seen_obj.add(unique_key)

        output_creator.finished("2/2")
        new_session.commit()
                        
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
        old_session.close()

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):

    convert_domain_evidence(old_session_maker, new_session_maker)
