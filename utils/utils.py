'''
Created on Mar 12, 2013

@author: kpaskov
'''

#Create evidence tables
def create_grouped_evidence_table(evidences, evidence_map, f):
    group_term_bioent_biocon = {}
    group_term_to_all_evidence = {}
   
    for evidence in evidences:
        group_term = evidence_map[evidence.id]
        if evidence.type == 'BIOCON_EVIDENCE':
            bb = evidence.bioent_biocon
        elif evidence.type == 'BIOREL_EVIDENCE':
            bb = evidence.biorel
            
        if not isinstance(group_term, list):
            group_term_bioent_biocon[group_term] = bb
            if group_term in group_term_to_all_evidence:
                group_term_to_all_evidence[group_term].append(evidence)
            else:
                group_term_to_all_evidence[group_term] = [evidence]
        else:
            for gt in group_term:
                group_term_bioent_biocon[gt] = bb
                if gt in group_term_to_all_evidence:
                    group_term_to_all_evidence[gt].append(evidence)
                else:
                    group_term_to_all_evidence[gt] = [evidence]
        
    table = []
    for (group_term, bioent_biocon) in group_term_bioent_biocon.iteritems():
        ev_for_group = group_term_to_all_evidence[group_term]
        entries = f(ev_for_group, group_term, bioent_biocon)
        table.append(entries)     
    return table

def create_phenotype_note(qualifiers):
    #ordered_qualifiers = ['increased', 'increased rate', 'increased duration', 'premature', 'normal', 'normal rate', 'abnormal', 'arrested', 'absent', 'delayed', 'decreased duration', 'decreased rate', 'decreased']        
    increased_quals = set(['increased', 'increased rate', 'increased duration', 'premature'])
    decreased_quals = set(['delayed', 'decreased duration', 'decreased rate', 'decreased'])
    messages = []

    #for qual in ordered_qualifiers:
    #    count = len([x for x in qualifiers if x == qual])
    #    if count > 0:
    #        messages.append(str(count) + ' ' + qual)
    
    inc_count = 0
    dec_count = 0
    for qual in qualifiers:
        if qual in increased_quals:
            inc_count = inc_count + 1
        if qual in decreased_quals:
            dec_count = dec_count + 1

    if inc_count > 0:
        messages.append(str(inc_count) + unichr(11014))
    if dec_count > 0:
        messages.append(str(dec_count) + unichr(11015))
    
    message = ', '.join(messages)
    if len(message) > 0:
        return '(' + message + ')'
    else:
        return ''
    
def entry_with_link(entry_name, link):
    return"<a href='" + link + "'>" + entry_name + "</a>"

def entry_with_note(entry_name, note):
    return "<span>" + entry_name + "</span><span class='muted' style='float:right'>" + note + "</span>"