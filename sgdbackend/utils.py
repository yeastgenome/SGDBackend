'''
Created on Mar 12, 2013

@author: kpaskov
'''
from sgdbackend.cache import get_cached_reference, get_cached_bioent
from sgdbackend_query.query_reference import get_references
from string import upper

def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def make_reference_list(bioent_ref_types, bioent_id, only_primary=False):
    reference_ids = set()
    for bioent_ref_type in bioent_ref_types:
        reference_ids.update([x.reference_id for x in get_references(bioent_ref_type, bioent_id=bioent_id)])
        
    if only_primary:
        primary_ids = set([x.reference_id for x in get_references('PRIMARY_LIT_EVIDENCE', bioent_id=bioent_id)])
        reference_ids.intersection_update(primary_ids)

    references = [get_cached_reference(reference_id) for reference_id in reference_ids]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references

def get_bioent_by_name(bioent_name, to_ignore):
    if bioent_name not in to_ignore:
        bioent = get_cached_bioent(bioent_name, 'LOCUS')
        if bioent is None:
            bioent = get_cached_bioent(bioent_name, 'BIOENTITY')
        if bioent is None and bioent_name.endswith('P'):
            bioent = get_cached_bioent(bioent_name[:-1] + 'p', 'PROTEIN')    
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

if __name__ == "__main__":
    print link_gene_names('ACT1 is my favorite gene. Act1 is the best. I really like act1.')
    