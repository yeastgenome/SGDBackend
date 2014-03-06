'''
Created on Mar 12, 2013

@author: kpaskov
'''
from datetime import datetime
from string import upper
import logging

from mpmath import ceil


def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def get_bioent_by_name(bioent_name, to_ignore):
    from model_new_schema.bioentity import Bioentity
    from sgdbackend_utils.cache import get_obj, get_word_to_bioent_id
    if bioent_name not in to_ignore:
        try:
            int(bioent_name)
        except ValueError:
            bioent_id = get_word_to_bioent_id(bioent_name)
            return None if bioent_id is None else get_obj(Bioentity, bioent_id)
    return None

def link_gene_names(text, to_ignore=set()):
    words = text.split(' ')
    new_chunks = []
    chunk_start = 0
    i = 0
    for word in words:
        if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-'):
            bioent_name = word[:-1]
        else:
            bioent_name = word
        
        bioent = get_bioent_by_name(upper(bioent_name), to_ignore)
            
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
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.ERROR)
    log = logging.getLogger(label)
    
    if log_directory is not None:
        hdlr = logging.FileHandler(log_directory + '/' + label + '.' + str(datetime.now().date()) + '.txt')
        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
        hdlr.setFormatter(formatter)
    else:
        hdlr = logging.NullHandler()
    log.addHandler(hdlr) 
    log.setLevel(logging.INFO)
    log.propagate = False
    return log
