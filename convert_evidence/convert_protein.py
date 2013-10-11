'''
Created on Sep 20, 2013

@author: kpaskov
'''
from convert_utils import create_or_update, set_up_logging, break_up_file, \
    create_format_name, prepare_connections
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
import logging
import sys

#Recorded times: 
  
"""
--------------------- Convert Domain ---------------------
"""

def create_domain(row):
    from model_new_schema.protein import Domain
    
    source = row[13].strip()
    format_name = create_format_name(row[3].strip())
    display_name = row[3].strip()
    description = row[4].strip()
    interpro_id = row[5].strip()
    interpro_description = row[6].strip()
    
    #Need to check these links
    if source == 'JASPAR':
        link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name
    elif source == 'HMMSmart':
        source = 'SMART'
        link = "http://smart.embl-heidelberg.de/smart/do_annotation.pl?DOMAIN=" + display_name
    elif source == 'HMMPfam':
        source = 'Pfam'
        link = "http://pfam.sanger.ac.uk/family?type=Family&entry=" + display_name
    elif source == 'Gene3D':
        link = "http://www.cathdb.info/version/latest/superfamily/" + display_name[6:]
    elif source == 'superfamily':
        source = 'SUPERFAMILY'
        link = "http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid=" + display_name
    elif source == 'Seg':
        link = None
    elif source == 'Coil':
        link = None
    elif source == 'HMMPanther':
        source = 'PANTHER'
        link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + display_name
    elif source == 'HMMTigr':
        source = 'TIGRFAMs'
        link = "http://cmr.tigr.org/tigr-scripts/CMR/HmmReport.cgi?hmm_acc=" + display_name
    elif source == 'FPrintScan':
        source = 'PRINTS'
        link = "http:////www.bioinf.man.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?display_opts=Prints&amp;category=None&amp;queryform=false&amp;prints_accn=" + display_name
    elif source == 'BlastProDom':
        source = 'ProDom'
        link = "http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&amp;query=" + display_name
    elif source == 'HMMPIR':
        source = "PIR superfamily"
        link = "http://pir.georgetown.edu/cgi-bin/ipcSF?" + display_name
    elif source == 'ProfileScan':
        source = 'PROSITE'
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
    elif source == 'PatternScan':
        source = 'PROSITE'
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
    else:
        print 'No link for source = ' + source + ' ' + str(display_name)
        return None
    
    if description == 'no description':
        description = None
    if interpro_description == 'NULL':
        interpro_description = None
    
    domain = Domain(format_name, display_name, description, interpro_id, interpro_description, link, source)
    return [domain]

def create_domain_from_tf_file(row):
    from model_new_schema.protein import Domain
    
    source = 'JASPAR'
    display_name = row[0]
    format_name = create_format_name(row[0])
    description = 'Class: ' + row[4] + ', Family: ' + row[3]
    interpro_id = None
    interpro_description = None
    
    link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name
    
    domain = Domain(format_name, display_name, description, interpro_id, interpro_description, link, source)
    return [domain]

def convert_domain(new_session_maker, chunk_size):
    from model_new_schema.protein import Domain as Domain
    
    log = logging.getLogger('convert.protein.domain')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Domain).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['display_name', 'description', 'interpro_id', 'interpro_description', 'link']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        data = break_up_file('/Users/kpaskov/final/yeastmine_protein_domains.tsv')
        
        used_unique_keys = set()   
        
        min_id = 0
        count = len(data)
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            old_objs = data[min_id:min_id+chunk_size]
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_domain(old_obj)
                    
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        if unique_key not in used_unique_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            used_unique_keys.add(unique_key)
                            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
            
        #Grab JASPAR domains from file
        old_objs = break_up_file('/Users/kpaskov/final/TF_family_class_accession04302013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_from_tf_file(old_obj)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    used_unique_keys.add(unique_key)
                        
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                        
        output_creator.finished("1/1")
        new_session.commit()
                        
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
--------------------- Convert Domain Evidence ---------------------
"""

def create_domain_evidence_id(row_id):
    return row_id + 80000000

def create_domain_evidence(row, row_id, key_to_bioentity, key_to_domain):
    from model_new_schema.protein import Domainevidence
    
    bioent_format_name = row[1].strip()
    source = row[13].strip()
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
    protein_id = key_to_bioentity[bioent_key].id
    
    if source == 'HMMSmart':
        source = 'SMART'
    if source == 'HMMPanther':
        source = 'PANTHER'
    if source == 'FPrintScan':
        source = 'PRINTS'
    if source == 'HMMPfam':
        source = 'Pfam'
    if source == 'PatternScan' or source == 'ProfileScan':
        source = 'PROSITE'
    if source == 'BlastProDom':
        source = 'ProDom'
    if source == 'HMMTigr':
        source = 'TIGRFAMs'
    if source == 'HMMPIR':
        source = 'PIR superfamily'
    
    if domain_format_name not in key_to_domain:
        print 'Domain not found. ' + domain_format_name
        return None
    domain_id = key_to_domain[domain_format_name].id
    
    #S288C
    strain_id = 1
    
    domain_evidence = Domainevidence(create_domain_evidence_id(row_id), None, strain_id, source, 
                                     int(start), int(end), evalue, status, date_of_run, protein_id, domain_id, None, None)
    return [domain_evidence]

def create_domain_evidence_from_tf_file(row, row_id, key_to_bioentity, key_to_domain, pubmed_id_to_reference_id):
    from model_new_schema.protein import Domainevidence
    
    bioent_format_name = row[2]
    source = 'JASPAR'
    db_identifier = row[0]
    start = 1
    evalue = None
    status = 'T'
    date_of_run = None
    pubmed_id = row[6]
    
    bioent_key = (bioent_format_name + 'P', 'PROTEIN')
    if bioent_key not in key_to_bioentity:
        print 'Protein not found. ' + bioent_format_name + 'P'
        return None
    protein = key_to_bioentity[bioent_key]
    protein_id = protein.id
    end = protein.length
    
    reference_id = None
    if pubmed_id in pubmed_id_to_reference_id:
        reference_id = pubmed_id_to_reference_id[pubmed_id]
    
    domain_key = db_identifier
    if domain_key not in key_to_domain:
        print 'Domain not found. ' + str(domain_key)
    domain_id = key_to_domain[domain_key].id
    
    #S288C
    strain_id = 1
    
    domain_evidence = Domainevidence(create_domain_evidence_id(row_id), reference_id, strain_id, source, 
                                     start, end, evalue, status, date_of_run, protein_id, domain_id, None, None)
    return [domain_evidence]

def convert_domain_evidence(new_session_maker, chunk_size):
    from model_new_schema.protein import Domain, Domainevidence
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.reference import Reference
    
    log = logging.getLogger('convert.protein.domain_evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Domainevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['reference_id', 'strain_id', 'source', 'date_created', 'created_by',
                           'start', 'end', 'evalue', 'status', 'date_of_run', 'protein_id', 'domain_id']
        
        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])       
        key_to_domain = dict([(x.unique_key(), x) for x in new_session.query(Domain).all()]) 
        pubmed_id_to_reference_id = dict([(x.pubmed_id, x.id) for x in new_session.query(Reference).all()]) 
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        data = break_up_file('/Users/kpaskov/final/yeastmine_protein_domains.tsv')
        
        used_unique_keys = set()   
        
        j=0
        min_id = 0
        count = len(data)
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            old_objs = data[min_id:min_id+chunk_size]
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_domain_evidence(old_obj, j, key_to_bioentity, key_to_domain)
                    
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = (newly_created_obj.protein_id, newly_created_obj.domain_id, newly_created_obj.start,
                                      newly_created_obj.end, newly_created_obj.evalue)
                        if unique_key not in used_unique_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if newly_created_obj.id not in key_to_current_obj else key_to_current_obj[newly_created_obj.id]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            used_unique_keys.add(unique_key)
                            
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                j = j+1
                            
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
            
        #Grab JASPAR evidence from file
        old_objs = break_up_file('/Users/kpaskov/final/TF_family_class_accession04302013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_evidence_from_tf_file(old_obj, j, key_to_bioentity, key_to_domain, pubmed_id_to_reference_id)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in used_unique_keys:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        used_unique_keys.add(unique_key)
                        
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
            j = j+1
                        
        output_creator.finished("1/1")
        new_session.commit()
                        
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

def convert(old_session_maker, new_session_maker):  
    log = set_up_logging('convert.protein')
    log.info('begin')
        
    convert_domain(new_session_maker, 5000)
    
    convert_domain_evidence(new_session_maker, 5000)
    
    log.info('complete')
    
if __name__ == "__main__":
    old_session_maker, new_session_maker = prepare_connections()
    convert(old_session_maker, new_session_maker)   
    
    