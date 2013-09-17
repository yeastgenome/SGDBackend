'''
Created on Mar 12, 2013

@author: kpaskov
'''
from sgdbackend_query.query_reference import get_references
from sgdbackend.cache import get_cached_reference

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
