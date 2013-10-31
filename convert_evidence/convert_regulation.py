'''
Created on Sep 10, 2013

@author: kpaskov
'''
from convert_other.convert_auxiliary import convert_bioentity_reference, \
    convert_interaction
from convert_utils import create_or_update, set_up_logging, create_format_name, \
    break_up_file, prepare_connections
from convert_utils.output_manager import OutputCreator
from mpmath import ceil, floor
import logging
import sys

#Recorded times:
#First Load (sgd-ng1): 28:31
#Maitenance (sgd-ng1): 

"""
--------------------- Convert Evidence ---------------------
"""
pubmed_to_strain = {#11504737: 'Other',
                    12006656: 'S288C',
                    15192094: 'W303',
                    #15647283: 'Other',
                    #16415340: 'Other',
                    16522208: 'W303',
                    17417638: 'S288C',
                    18524923: 'CEN.PK',
                    #21177862: 'Other',
                    21329885: 'S288C',
                    22114689: 'S288C',
                    22189861: 'S288C',
                    22384390: 'Sigma1278b',
                    22438580: 'W303',
                    22498630: 'S288C',
                    22616008: 'S288C',
                    20195295: 'S288C'}

def create_evidence(row, key_to_experiment, key_to_bioent, pubmed_to_reference, key_to_source, key_to_strain):
    from model_new_schema.evidence import Regulationevidence
    
    #bioent1_gene_name = row[0]
    bioent1_format_name = row[1].upper().strip()
    bioent2_format_name = row[3].upper().strip()
    experiment_format_name = create_format_name(row[4].strip())
    experiment_eco_id = row[5].strip()
    condition_value = row[6].strip()
    #unknown_field1 = row[7]
    #unknown_field2 = row[8]
    #unknown_field3 = row[9]
    pubmed_id = int(row[10].strip())
    source_key = row[11].strip()
    
    bioent1_key = (bioent1_format_name, 'LOCUS') 
    bioent1 = None if bioent1_key not in key_to_bioent else key_to_bioent[bioent1_key]
    
    bioent2_key = (bioent2_format_name, 'LOCUS') 
    bioent2 = None if bioent2_key not in key_to_bioent else key_to_bioent[bioent2_key]
    
    experiment = None if experiment_format_name not in key_to_experiment else key_to_experiment[experiment_format_name]
    if experiment is None:
        experiment = None if experiment_eco_id not in key_to_experiment else key_to_experiment[experiment_eco_id]
    reference = None if pubmed_id not in pubmed_to_reference else pubmed_to_reference[pubmed_id]
    strain = None if pubmed_id not in pubmed_to_strain else key_to_strain[pubmed_to_strain[pubmed_id]]
    source = None if source_key not in key_to_source else key_to_source[source_key]
    
    conditions = []
    if condition_value != '""':
        from model_new_schema.condition import Generalcondition
        condition_value = condition_value.replace('??', "\00b5")
        conditions.append(Generalcondition(condition_value))

    
    new_evidence = Regulationevidence(source, reference, strain, experiment, None, 
                                      bioent1, bioent2, conditions, None, None)
    return [new_evidence]

def convert_evidence(new_session_maker, chunk_size):
    from model_new_schema.evidence import Regulationevidence
    from model_new_schema.evelements import Experiment, Source, Strain
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.reference import Reference
    
    log = logging.getLogger('convert.regulation.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id', 
                       'bioentity1_id', 'bioentity2_id']
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(Experiment).all()])
        key_to_bioent = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        pubmed_to_reference = dict([(x.pubmed_id, x) for x in new_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
                
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        
        old_obj_chunks = [[] for _ in range(num_chunks)]
        f = open('data/yeastmine_regulation.tsv', 'r')
        for line in f:
            row = line.split('\t')
            bioent1_format_name = row[1].upper().strip()
            bioent1_key = (bioent1_format_name, 'LOCUS') 
            bioent1 = None if bioent1_key not in key_to_bioent else key_to_bioent[bioent1_key]
            if bioent1 is not None:
                index = int(min(num_chunks-1, int(floor(1.0*(bioent1.id-min_bioent_id)/chunk_size))))
                old_obj_chunks[index].append(row)
        f.close()
        
        for i in range(0, num_chunks):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
            
            old_objs = old_obj_chunks[i]
            
            #Grab all current objects
            if i < num_chunks-1:
                current_objs = new_session.query(Regulationevidence).filter(Regulationevidence.bioentity1_id >= min_id).filter(
                                                                        Regulationevidence.bioentity1_id < max_id).all()
            else:
                current_objs = new_session.query(Regulationevidence).filter(Regulationevidence.bioentity1_id >= min_id).all()
                                        
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = id_to_current_obj.keys()
            already_seen = set()
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, key_to_experiment, key_to_bioent, pubmed_to_reference, key_to_source, key_to_strain)
         
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
                    else:
                        print unique_key
                        
            #Delete untouched objs
            for untouched_obj  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj])
                output_creator.removed()
                
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        
    log.info('complete')

"""
--------------------- Convert Paragraph ---------------------
"""

def create_paragraph(row, key_to_bioentity, key_to_source):
    from model_new_schema.paragraph import Paragraph
    
    bioent_format_name = row[0]
    bioent_key = (bioent_format_name, 'LOCUS')
    bioent = None if bioent_key not in key_to_bioentity else key_to_bioentity[bioent_key]
    source = key_to_source['SGD']
    
    text = row[2]
    
    paragraph = Paragraph('REGULATION', source, bioent, text, None, None)
    return [paragraph]

def convert_paragraph(new_session_maker):
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.paragraph import Paragraph
    from model_new_schema.evelements import Source
    
    log = logging.getLogger('convert.regulation.paragraph')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['text'] 
        
        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])       
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])    
        
        #Grab all current objects
        current_objs = new_session.query(Paragraph).filter(Paragraph.class_type == 'REGULATION').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        untouched_obj_ids = set(id_to_current_obj.keys())

        old_objs = break_up_file('data/Reg_Summary_Paragraphs04282013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph(old_obj, key_to_bioentity, key_to_source)
     
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                
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
--------------------- Convert ParagraphReference ---------------------
"""

def create_paragraph_reference(row, key_to_bioentity, key_to_paragraph, pubmed_id_to_reference, key_to_source):
    from model_new_schema.paragraph import ParagraphReference
    
    bioent_format_name = row[0]
    bioent_key = (bioent_format_name, 'LOCUS')
    if bioent_key not in key_to_bioentity:
        bioent_key = (bioent_format_name, 'BIOENTITY')
        if bioent_key not in key_to_bioentity:
            print 'Bioentity does not exist. ' + str(bioent_format_name)
            return None
    bioent = key_to_bioentity[bioent_key]
    
    paragraph_key = (bioent.format_name, 'REGULATION')
    if paragraph_key not in key_to_paragraph:
        print 'Paragraph does nto exist. ' + str(paragraph_key)
        return None
    paragraph = key_to_paragraph[paragraph_key]
    
    paragraph_references = []
    
    pubmed_ids = row[3].split('|')
    for pubmed_id in pubmed_ids:
        num_pubmed_id = ''
        if pubmed_id != '':
            num_pubmed_id = int(pubmed_id.strip())
        if num_pubmed_id not in pubmed_id_to_reference:
            print 'Reference does not exist. ' + str(num_pubmed_id)
            return None
        reference = pubmed_id_to_reference[num_pubmed_id]
        source = key_to_source['SGD']
        paragraph_references.append(ParagraphReference(source, paragraph, reference, 'REGULATION', None, None))
        
   
    return paragraph_references

def convert_paragraph_reference(new_session_maker):
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.paragraph import Paragraph, ParagraphReference
    from model_new_schema.evelements import Source
    from model_new_schema.reference import Reference
    
    log = logging.getLogger('convert.regulation.paragraph_reference')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = [] 
        
        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])   
        key_to_paragraph = dict([(x.unique_key(), x) for x in new_session.query(Paragraph).filter(Paragraph.class_type == 'REGULATION').all()])    
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in new_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])   
        
        #Grab all current objects
        current_objs = new_session.query(ParagraphReference).filter(ParagraphReference.class_type == 'REGULATION').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        used_unique_keys = set()  

        old_objs = break_up_file('data/Reg_Summary_Paragraphs04282013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph_reference(old_obj, key_to_bioentity, key_to_paragraph, pubmed_id_to_reference, key_to_source)
     
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
    log = set_up_logging('convert.regulation')
    
    log.info('begin')
    
    convert_evidence(new_session_maker, 300)    
        
    from model_new_schema.evidence import Regulationevidence
    get_bioent_ids_f = lambda x: [x.bioentity1_id, x.bioentity2_id]
    
    convert_paragraph(new_session_maker)
    
    convert_paragraph_reference(new_session_maker)
    
    convert_interaction(new_session_maker, Regulationevidence, 'REGULATION', 'convert.regulation.interaction', 10000, True)
    
    convert_bioentity_reference(new_session_maker, Regulationevidence, 'REGULATION', 'convert.regulation.bioentity_reference', 10000, get_bioent_ids_f)
            
    log.info('complete')
    
if __name__ == "__main__":
    new_session_maker = prepare_connections(need_old=False)
    convert(new_session_maker)
    