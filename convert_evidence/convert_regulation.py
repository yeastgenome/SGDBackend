'''
Created on Sep 10, 2013

@author: kpaskov
'''
from convert_aux.auxillary_tables import convert_bioentity_reference
from convert_utils import create_or_update, set_up_logging, prepare_schema_connection, \
    create_format_name, break_up_file
from mpmath import ceil
from convert_utils.output_manager import OutputCreator
import logging
import model_new_schema
import sys

#Recorded times:
#First Load (sgd-ng1): 28:31
#Maitenance (sgd-ng1): 

"""
--------------------- Convert Evidence ---------------------
"""
def create_evidence_id(old_regevidence_id):
    return old_regevidence_id + 40000000

pubmed_to_strain = {11504737: 27,
                    12006656: 1,
                    15192094: 21,
                    15647283: 27,
                    16415340: 27,
                    16522208: 21,
                    17417638: 1,
                    18524923: 8,
                    21177862: 27,
                    21329885: 1,
                    22114689: 1,
                    22189861: 1,
                    22384390: 2,
                    22438580: 21,
                    22498630: 1,
                    22616008: 1,
                    20195295: 1}

def create_evidence(row, row_id, key_to_experiment, key_to_bioent, pubmed_to_reference_id):
    from model_new_schema.regulation import Regulationevidence
    
    #bioent1_gene_name = row[0]
    bioent1_format_name = row[1].upper().strip()
    bioent2_format_name = row[3].upper().strip()
    experiment_format_name = create_format_name(row[4].strip())
    experiment_eco_id = row[5].strip()
    conditions = row[6].strip()
    #unknown_field1 = row[7]
    #unknown_field2 = row[8]
    #unknown_field3 = row[9]
    pubmed_id = int(row[10].strip())
    source = row[11].strip()
    
    if (bioent1_format_name, 'LOCUS') in key_to_bioent:
        bioent1 = key_to_bioent[(bioent1_format_name, 'LOCUS')]
    elif (bioent1_format_name, 'BIOENTITY') in key_to_bioent:
        bioent1 = key_to_bioent[(bioent1_format_name, 'BIOENTITY')]
    else:
        print 'Bioent does not exist ' + str(bioent1_format_name)
        return None
    bioent1_id = bioent1.id
    
    if (bioent2_format_name, 'LOCUS') in key_to_bioent:
        bioent2 = key_to_bioent[(bioent2_format_name, 'LOCUS')]
    elif (bioent2_format_name, 'BIOENTITY') in key_to_bioent:
        bioent2 = key_to_bioent[(bioent2_format_name, 'BIOENTITY')]
    else:
        print 'Bioent does not exist ' + str(bioent2_format_name)
        return None
    bioent2_id = bioent2.id
    
    experiment_key = experiment_format_name
    if experiment_key not in key_to_experiment:
        experiment_key = create_format_name(experiment_eco_id)
        if experiment_key not in key_to_experiment:
            print 'Experiment does not exist ' + str(experiment_key)
            return None
    experiment_id = key_to_experiment[experiment_key].id
    
    if pubmed_id not in pubmed_to_reference_id:
        print 'Reference does not exist ' + str(pubmed_id)
        return None
    reference_id = pubmed_to_reference_id[pubmed_id]
    
    if conditions == '""':
        conditions = None
    else:
        conditions.replace('??', "\00b5")
        
    strain_id = None
    if pubmed_id in pubmed_to_strain:
        strain_id = pubmed_to_strain[pubmed_id]
    
    new_evidence = Regulationevidence(create_evidence_id(row_id), experiment_id, reference_id, strain_id, source, 
                                      bioent1_id, bioent2_id, conditions, 
                                      None, None)
    return [new_evidence]

def convert_evidence(new_session_maker, chunk_size):
    from model_new_schema.regulation import Regulationevidence
    from model_new_schema.evelement import Experiment
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.reference import Reference
    
    log = logging.getLogger('convert.regulation.evidence')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source', 'conditions', 
                       'bioentity1_id', 'bioentity2_id', 'date_created', 'created_by']
        
        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(Experiment).all()])
        key_to_bioent = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        pubmed_to_reference_id = dict([(x.pubmed_id, x.id) for x in new_session.query(Reference).all()])
        
        #Grab old objects
        data = break_up_file('/Users/kpaskov/final/yeastmine_regulation.tsv')
                
        count = len(data)
        num_chunks = ceil(1.0*count/chunk_size)
        min_id = 0
        j = 0
        for i in range(0, num_chunks):
            #Grab all current objects
            current_objs = new_session.query(Regulationevidence).filter(Regulationevidence.id >= create_evidence_id(min_id)).filter(Regulationevidence.id < create_evidence_id(min_id+chunk_size)).all()
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())

            old_objs = data[min_id:min_id+chunk_size]
        
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, j, key_to_experiment, key_to_bioent, pubmed_to_reference_id)
         
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
                j = j + 1
                
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size
        
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        
    log.info('complete')

"""
--------------------- Convert Paragraph ---------------------
"""

def create_paragraph(row, key_to_bioentity):
    from model_new_schema.bioentity import Paragraph
    
    bioent_format_name = row[0]
    bioent_key = (bioent_format_name, 'LOCUS')
    if bioent_key not in key_to_bioentity:
        bioent_key = (bioent_format_name, 'BIOENTITY')
        if bioent_key not in key_to_bioentity:
            print 'Bioentity does not exist. ' + str(bioent_format_name)
            return None
    bioent_id = key_to_bioentity[bioent_key].id
    
    text = row[2]
    
    paragraph = Paragraph(bioent_id, 'REGULATION', text, None, None)
    return [paragraph]

def convert_paragraph(new_session_maker):
    from model_new_schema.bioentity import Bioentity, Paragraph
    
    log = logging.getLogger('convert.regulation.paragraph')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:   
        new_session = new_session_maker()
         
        #Values to check
        values_to_check = ['text', 'date_created', 'created_by'] 
        
        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])       
        
        #Grab all current objects
        current_objs = new_session.query(Paragraph).filter(Paragraph.class_type == 'REGULATION').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        untouched_obj_ids = set(id_to_current_obj.keys())

        old_objs = break_up_file('/Users/kpaskov/final/Reg_Summary_Paragraphs04282013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph(old_obj, key_to_bioentity)
     
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

def create_paragraph_reference(row, key_to_bioentity, paragraph_key_to_id, pubmed_id_to_reference_id):
    from model_new_schema.bioentity import ParagraphReference
    
    bioent_format_name = row[0]
    bioent_key = (bioent_format_name, 'LOCUS')
    if bioent_key not in key_to_bioentity:
        bioent_key = (bioent_format_name, 'BIOENTITY')
        if bioent_key not in key_to_bioentity:
            print 'Bioentity does not exist. ' + str(bioent_format_name)
            return None
    bioent_id = key_to_bioentity[bioent_key].id
    
    paragraph_key = ('REGULATION', bioent_id)
    if paragraph_key not in paragraph_key_to_id:
        print 'Paragraph does nto exist. ' + str(paragraph_key)
        return None
    paragraph_id = paragraph_key_to_id[paragraph_key]
    
    paragraph_references = []
    
    pubmed_ids = row[3].split('|')
    for pubmed_id in pubmed_ids:
        num_pubmed_id = ''
        if pubmed_id != '':
            num_pubmed_id = int(pubmed_id.strip())
        if num_pubmed_id not in pubmed_id_to_reference_id:
            print 'Reference does not exist. ' + str(num_pubmed_id)
            return None
        reference_id = pubmed_id_to_reference_id[num_pubmed_id]
        paragraph_references.append(ParagraphReference(paragraph_id, reference_id, 'REGULATION'))
        
   
    return paragraph_references

def convert_paragraph_reference(new_session_maker):
    from model_new_schema.bioentity import Bioentity, Paragraph, ParagraphReference
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
        paragraph_key_to_id = dict([(x.unique_key(), x.id) for x in new_session.query(Paragraph).filter(Paragraph.class_type == 'REGULATION').all()])    
        pubmed_id_to_reference_id = dict([(x.pubmed_id, x.id) for x in new_session.query(Reference).all()])
        
        #Grab all current objects
        current_objs = new_session.query(ParagraphReference).filter(ParagraphReference.class_type == 'REGULATION').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        used_unique_keys = set()  

        old_objs = break_up_file('/Users/kpaskov/final/Reg_Summary_Paragraphs04282013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph_reference(old_obj, key_to_bioentity, paragraph_key_to_id, pubmed_id_to_reference_id)
     
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
    
    convert_evidence(new_session_maker, 10000)    
        
    from model_new_schema.regulation import Regulationevidence
    get_bioent_ids_f = lambda x: [x.bioentity1_id, x.bioentity2_id]
    
    convert_paragraph(new_session_maker)
    
    convert_paragraph_reference(new_session_maker)
    
    convert_bioentity_reference(new_session_maker, Regulationevidence, 'REGULATION', 'convert.regulation.bioentity_reference', 10000, get_bioent_ids_f)
            
    log.info('complete')
    
if __name__ == "__main__":
    from convert_all import new_config
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    convert(new_session_maker, False)
    