'''
Created on Sep 20, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, break_up_file, create_format_name
from convert_utils.output_manager import OutputCreator
from mpmath import ceil, floor
import logging
import sys

#Recorded times: 
  

 
"""
--------------------- Convert Domain Evidence ---------------------
"""

def create_domain_evidence(row, key_to_bioentity, key_to_domain, key_to_strain, key_to_source):
    from model_new_schema.evidence import Domainevidence
    
    bioent_format_name = row[1].strip()
    source_name = row[13].strip()
    domain_format_name = create_format_name(row[3].strip())
    start = row[10].strip()
    end = row[11].strip()
    evalue = row[12].strip()
    status = None
    date_of_run = None
    
    bioent_key = (bioent_format_name + 'P', 'PROTEIN')
    if bioent_key not in key_to_bioentity:
        print 'Protein not found. ' + bioent_format_name + 'P'
        return None
    protein = key_to_bioentity[bioent_key]
    
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
                                     int(start), int(end), evalue, status, date_of_run, protein, domain, None, None)
    return [domain_evidence]

def create_domain_evidence_from_tf_file(row, key_to_bioentity, key_to_domain, pubmed_id_to_reference, key_to_strain, key_to_source):
    from model_new_schema.evidence import Domainevidence
    
    bioent_format_name = row[2].strip()
    source_name = 'JASPAR'
    db_identifier = row[0]
    start = 1
    evalue = None
    status = 'T'
    date_of_run = None
    pubmed_id = row[6]
    
    bioent_key = (bioent_format_name + 'P', 'PROTEIN')
    protein = None if bioent_key not in key_to_bioentity else key_to_bioentity[bioent_key]
    if protein is None:
        print bioent_key
        return []
    end = protein.length
    
    domain_key = (db_identifier, 'DOMAIN')
    domain = None if domain_key not in key_to_domain else key_to_domain[domain_key]
    strain = key_to_strain['S288C']
    source = None if source_name not in key_to_source else key_to_source[source_name]
    reference = None if pubmed_id not in pubmed_id_to_reference else pubmed_id_to_reference[pubmed_id]
    
    domain_evidence = Domainevidence(source, reference, strain, None, 
                                     start, end, evalue, status, date_of_run, protein, domain, None, None)
    return [domain_evidence]

def convert_domain_evidence(new_session_maker, chunk_size):
    from model_new_schema.evidence import Domain, Domainevidence
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.reference import Reference
    from model_new_schema.evelements import Source, Strain
    
    log = logging.getLogger('convert.protein_domain.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
                
        #Values to check
        values_to_check = ['reference_id', 'strain_id', 'source_id', 'reference_id', 'strain_id',
                           'start', 'end', 'evalue', 'status', 'date_of_run']
        
        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])       
        key_to_domain = dict([(x.unique_key(), x) for x in new_session.query(Domain).all()]) 
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in new_session.query(Reference).all()]) 
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        
        untouched_obj_ids = dict()
        already_seen_obj = set()
        
        #Grab old objects
        data = break_up_file('data/yeastmine_protein_domains.tsv')
        
        min_protein_id = 200000
        max_protein_id = 210000
        num_chunks = ceil(1.0*(max_protein_id-min_protein_id)/chunk_size)
        
        #Break into chunks
        data_chunks = [[] for x in range(0, num_chunks)]
        for row in data:
            bioent_format_name = row[1].strip()
            bioent_key = (bioent_format_name + 'P', 'PROTEIN')
            protein = None if bioent_key not in key_to_bioentity else key_to_bioentity[bioent_key]
            if protein is not None:
                index = int(min(num_chunks-1, int(floor(1.0*(protein.id-min_protein_id)/chunk_size))))
                data_chunks[index].append(row)


        for i in range(0, num_chunks):
            min_id = min_protein_id + i*chunk_size
            max_id = max_protein_id + (i+1)*chunk_size
            
            if i < num_chunks-1:
                current_objs = new_session.query(Domainevidence).filter(Domainevidence.bioentity_id >= min_id).filter(Domainevidence.bioentity_id < max_id).all()
            else:
                current_objs = new_session.query(Domainevidence).filter(Domainevidence.bioentity_id >= min_id).all()
                
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
            untouched_obj_ids.update(id_to_current_obj)
                        
            old_objs = data_chunks[i]
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
                            del untouched_obj_ids[current_obj_by_id.id]
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            del untouched_obj_ids[current_obj_by_key.id]
                    already_seen_obj.add(obj_key)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
            
        id_to_current_obj = dict([(x.id, x) for x in untouched_obj_ids.values()])
        key_to_current_obj = dict([(x.unique_key(), x) for x in untouched_obj_ids.values()])
            
        #Grab JASPAR evidence from file
        old_objs = break_up_file('data/TF_family_class_accession04302013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_evidence_from_tf_file(old_obj, key_to_bioentity, key_to_domain, pubmed_id_to_reference, key_to_strain, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in already_seen_obj:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        del untouched_obj_ids[current_obj_by_id.id]
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        del untouched_obj_ids[current_obj_by_key.id]
                else:
                    print unique_key
                already_seen_obj.add(unique_key)
                        
        output_creator.finished("1/1")
        new_session.commit()
                        
        #Delete untouched objs
        for untouched_obj  in untouched_obj_ids.values():
            new_session.delete(untouched_obj)
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

    convert_domain_evidence(new_session_maker, 1000)
        

    
    