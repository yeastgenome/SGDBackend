from sgdbackend_query import get_resources, query_locustabs, get_disambigs
from sgdbackend_query.query_reference import get_reference_bibs, get_references
from sgdbackend_utils.cache import id_to_bioent, id_to_reference, id_to_biocon
from sgdbackend_utils.obj_to_json import locustab_to_json, url_to_json, \
    disambig_to_json

#Disambigs
def make_all_disambigs(min_id, max_id):
    return [disambig_to_json(x) for x in get_disambigs(min_id, max_id)]
    
#Bioentity
def make_all_bioentities(min_id, max_id):
    bioents = []
    for bioent_id, bioent in id_to_bioent.iteritems():
        if (min_id is None or bioent_id >= min_id) and (max_id is None or bioent_id < max_id):
            bioents.append(bioent)
    return bioents

def make_bioentity_list(bioent_ids):
    bioents = []
    for bioent_id in bioent_ids:
        if bioent_id in id_to_bioent:
            bioents.append(id_to_bioent[bioent_id])
    return bioents

#Locus
def make_locustabs(bioent_id):
    locustab = query_locustabs(bioent_id)
    if locustab is None:
        return None
    else:
        return locustab_to_json(locustab)
    
#Bioconcept
def make_all_bioconcepts(min_id, max_id):
    biocons = []
    for biocon_id, biocon in id_to_biocon.iteritems():
        if (min_id is None or biocon_id >= min_id) and (max_id is None or biocon_id < max_id):
            biocons.append(biocon)
    return biocons

def make_bioconcept_list(biocon_ids):
    biocons = []
    for biocon_id in biocon_ids:
        if biocon_id in id_to_biocon:
            biocons.append(id_to_biocon[biocon_id])
    return biocons

#Reference
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

def make_all_bibentries(min_id, max_id):
    all_reference_bibs = get_reference_bibs(min_id=min_id, max_id=max_id)
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

    references = [id_to_reference[reference_id] for reference_id in reference_ids]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references

def make_resources(resource_type, bioent_id):
    resources = get_resources(resource_type, bioent_id=bioent_id)
    resources.sort(key=lambda x: x.display_name)
    return [url_to_json(url) for url in resources]



