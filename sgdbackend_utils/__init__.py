'''
Created on Mar 12, 2013

@author: kpaskov
'''
from datetime import datetime
from mpmath import ceil
from sgdbackend_query import get_obj_id, get_multi_obj_ids
from sgdbackend_utils.cache import id_to_bioent, id_to_reference
from string import upper
import logging

def make_references(bioent_ref_types, bioent_id, only_primary=False):
    from sgdbackend_query.query_auxiliary import get_bioentity_references
    reference_ids = set()
    for bioent_ref_type in bioent_ref_types:
        reference_ids.update([x.reference_id for x in get_bioentity_references(bioent_ref_type, bioent_id=bioent_id)])
        
    if only_primary:
        primary_ids = set([x.reference_id for x in get_bioentity_references('PRIMARY_LITERATURE', bioent_id=bioent_id)])
        reference_ids.intersection_update(primary_ids)

    references = [id_to_reference[reference_id] for reference_id in reference_ids]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references

def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def get_bioent_by_name(bioent_name, to_ignore, word_dict):
    if bioent_name not in to_ignore:
        bioent_ids = None if bioent_name not in word_dict else word_dict[bioent_name]
        bioent_id = None if bioent_ids is None or len(bioent_ids) == 0 else bioent_ids[0]
        if bioent_id is None and bioent_name.endswith('P'):
            bioent_id = get_obj_id(bioent_name[:-1], class_type='BIOENTITY', subclass_type='LOCUS')    
        return None if bioent_id is None else id_to_bioent[bioent_id]
    return None

def link_gene_names(text, to_ignore=set()):
    words = text.split(' ')
    prepped_words = [word[:-1].upper() if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-') else word for word in words]
    word_dict = get_multi_obj_ids(prepped_words, class_type='BIOENTITY', subclass_type='LOCUS')
    new_chunks = []
    chunk_start = 0
    i = 0
    for word in words:
        if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-'):
            bioent_name = word[:-1]
        else:
            bioent_name = word
        
        bioent = get_bioent_by_name(upper(bioent_name), to_ignore, word_dict)
            
        if bioent is not None:
            new_chunks.append(text[chunk_start: i])
            chunk_start = i + len(word) + 1
            
            new_chunk = "<a href='" + bioent['link'] + "'>" + bioent_name + "</a>"
            if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-'):
                new_chunk = new_chunk + word[-1]
            new_chunks.append(new_chunk)
        i = i + len(word) + 1
    new_chunks.append(text[chunk_start: i])
    try:
        return ' '.join(new_chunks)
    except:
        print text
        return text

    
    
#Used to break very large queries into a manageable size.
chunk_size = 500
def retrieve_in_chunks(ids, f):
    num_chunks = int(ceil(float(len(ids))/chunk_size))
    result = set()
    for i in range(0, num_chunks):
        min_index = i*chunk_size
        max_index = (i+1)*chunk_size
        if max_index > len(ids):
            chunk_ids = ids[min_index:]
        else:
            chunk_ids = ids[min_index:max_index]
        result.update(f(chunk_ids))
    return result

def set_up_logging(log_directory, label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO)
    log = logging.getLogger(label)
    
    if log_directory is not None:
        hdlr = logging.FileHandler(log_directory + '/' + label + '.' + str(datetime.now().date()) + '.txt')
        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
        hdlr.setFormatter(formatter)
    else:
        hdlr = logging.NullHandler()
    log.addHandler(hdlr) 
    log.setLevel(logging.INFO)
    return log
