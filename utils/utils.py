'''
Created on Mar 12, 2013

@author: kpaskov
'''

#Create evidence tables
def create_grouped_evidence_table(evidences, evidence_map, f):
    group_term_to_evid = {}
   
    for evidence in evidences:
        group_term = evidence_map[evidence.id]
                    
        if not isinstance(group_term, list):
            if group_term in group_term_to_evid:
                group_term_to_evid[group_term].append(evidence)
            else:
                group_term_to_evid[group_term] = [evidence]
        else:
            for gt in group_term:
                if gt in group_term_to_evid:
                    group_term_to_evid[gt].append(evidence)
                else:
                    group_term_to_evid[gt] = [evidence]
        
    table = []
    for (group_term, ev_for_group) in group_term_to_evid.iteritems():
        entries = f(ev_for_group, group_term)
        table.append(entries)     
    return table

def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def make_reference_list(evidences=None, references=None):
    if evidences is not None:
        references = set([evidence.reference for evidence in evidences if evidence.reference is not None])
    sorted_references = sorted(references, key=lambda x: x.display_name.lower())
    citations = [reference.citation for reference in sorted_references]
    return citations  
