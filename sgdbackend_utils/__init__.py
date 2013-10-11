'''
Created on Mar 12, 2013

@author: kpaskov
'''
from string import upper

def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def get_bioent_by_name(bioent_name, to_ignore):
    from sgdbackend_utils.cache import get_cached_bioent
    if bioent_name not in to_ignore:
        bioent = get_cached_bioent(bioent_name, 'LOCUS')
        if bioent is None and bioent_name.endswith('P'):
            bioent = get_cached_bioent(bioent_name[:-1], 'LOCUS')    
        return bioent
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
    return ' '.join(new_chunks)
    