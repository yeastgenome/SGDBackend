'''
Created on Mar 12, 2013

@author: kpaskov
'''
from query.query_reference import get_references
from sgdbackend.cache import get_cached_reference

##Create evidence tables
#def create_grouped_evidence_table(evidences, evidence_map, f):
#    group_term_to_evid = {}
#   
#    for evidence in evidences:
#        group_term = evidence_map[evidence.id]
#                    
#        if not isinstance(group_term, list):
#            if group_term in group_term_to_evid:
#                group_term_to_evid[group_term].append(evidence)
#            else:
#                group_term_to_evid[group_term] = [evidence]
#        else:
#            for gt in group_term:
#                if gt in group_term_to_evid:
#                    group_term_to_evid[gt].append(evidence)
#                else:
#                    group_term_to_evid[gt] = [evidence]
#        
#    table = []
#    for (group_term, ev_for_group) in group_term_to_evid.iteritems():
#        entries = f(ev_for_group, group_term)
#        table.append(entries)     
#    return table

def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def make_reference_list(bioent_ref_types, bioent_id):
    reference_ids = set()
    for bioent_ref_type in bioent_ref_types:
        reference_ids.update([x.reference_id for x in get_references(bioent_ref_type, bioent_id=bioent_id)])

    references = [get_cached_reference(reference_id) for reference_id in reference_ids]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references
