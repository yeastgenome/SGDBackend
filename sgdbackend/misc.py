from sgdbackend_query import query_bioentitytabs, get_resources
from sgdbackend_query.query_reference import get_reference_bibs, get_references
from sgdbackend_utils.cache import get_cached_bioent, id_to_bioent, \
    id_to_reference, get_cached_reference
from sgdbackend_utils.obj_to_json import bioentitytab_to_json, url_to_json


def make_bioentitytabs(bioent_id):
    bioentitytab = query_bioentitytabs(bioent_id)
    if bioentitytab is None:
        return None
    else:
        return bioentitytab_to_json(bioentitytab)
    
def make_all_bioents(min_id, max_id):
    bioents = {}
    for bioent in id_to_bioent.values():
        bioent_id = bioent['id']
        if min_id is not None:
            if bioent_id >= min_id and bioent_id < max_id:
                bioents[bioent_id] = bioent
        else:
            bioents[bioent_id] = bioent
    return bioents.values()

def make_bioent_list(bioent_ids):
    bioents = []
    for bioent_id in bioent_ids:
        bioent = get_cached_bioent(str(bioent_id), bioent_type='locus')
        if bioent is not None:
            bioents.append(bioent)
    return bioents

def make_all_references(min_id, max_id):
    references = {}
    for reference in id_to_reference.values():
        reference_id = reference['id']
        if min_id is not None:
            if reference_id >= min_id and reference_id < max_id:
                references[reference_id] = reference
        else:
            references[reference_id] = reference
    return references.values()

def make_all_bibentries():
    all_reference_bibs = get_reference_bibs()
    return [{'id': x.id, 'text': x.text} for x in all_reference_bibs]

def make_reference_list(reference_ids):
    ref_bibs = get_reference_bibs(reference_ids=reference_ids)
    references_json = [ref_bib.text for ref_bib in ref_bibs]
    return references_json

def make_references(bioent_ref_types, bioent_id, only_primary=False):
    reference_ids = set()
    for bioent_ref_type in bioent_ref_types:
        reference_ids.update([x.reference_id for x in get_references(bioent_ref_type, bioent_id=bioent_id)])
        
    if only_primary:
        primary_ids = set([x.reference_id for x in get_references('PRIMARY_LITERATURE', bioent_id=bioent_id)])
        reference_ids.intersection_update(primary_ids)

    references = [get_cached_reference(reference_id) for reference_id in reference_ids]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references

def make_resources(resource_type, bioent_id):
    resources = get_resources(resource_type, bioent_id=bioent_id)
    resources.sort(key=lambda x: x.display_name)
    return [url_to_json(url) for url in resources]



