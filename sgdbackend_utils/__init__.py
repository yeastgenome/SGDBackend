'''
Created on Mar 12, 2013

@author: kpaskov
'''
from sgdbackend_query import get_obj_id, get_multi_obj_ids
from sgdbackend_utils.cache import id_to_bioent
from string import upper

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
    return ' '.join(new_chunks)
    