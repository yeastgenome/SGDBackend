'''
Created on Mar 12, 2013

@author: kpaskov
'''

#Create evidence tables
def create_grouped_evidence_table(evidences, evidence_map, f):
    group_term__to_bb_and_ev = {}
   
    for evidence in evidences:
        group_term = evidence_map[evidence.id]
        if evidence.type == 'BIOCON_EVIDENCE':
            bb = evidence.bioent_biocon
        elif evidence.type == 'BIOREL_EVIDENCE':
            bb = evidence.biorel
                    
        if not isinstance(group_term, list):
            if group_term in group_term__to_bb_and_ev:
                group_term__to_bb_and_ev[group_term][1].append(evidence)
            else:
                group_term__to_bb_and_ev[group_term] = (bb, [evidence])
        else:
            for gt in group_term:
                if gt in group_term__to_bb_and_ev:
                    group_term__to_bb_and_ev[gt][1].append(evidence)
                else:
                    group_term__to_bb_and_ev[gt] = (bb, [evidence])
        
    table = []
    for (group_term, (bioent_biocon, ev_for_group)) in group_term__to_bb_and_ev.iteritems():
        entries = f(bioent_biocon, ev_for_group, group_term)
        table.append(entries)     
    return table

def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def make_reference_list(evidences):
    references = set([evidence.reference for evidence in evidences if evidence.reference is not None])
    sorted_references = sorted(references, key=lambda x: x.name)
    citations = [reference.citation for reference in sorted_references]
    return citations  

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
    
def create_note_from_pieces(pieces):
    pieces_to_count = {}
    for piece in pieces:
        if piece in pieces_to_count:
            pieces_to_count[piece] = pieces_to_count[piece] + 1
        else:
            pieces_to_count[piece] = 1
            
    messages = [str(value) + ' ' + key for (key, value) in pieces_to_count.iteritems()]
    message = ', '.join(sorted(messages))

    return '(' + message + ')'
    
def entry_with_link(entry_name, link):
    return"<a href='" + link + "'>" + entry_name + "</a>"

def entry_with_note(entry_name, note):
    return "<span>" + entry_name + "</span><span class='muted' style='float:right'>" + note + "</span>"

def float_approx_equal(x, y, tol=1e-18, rel=1e-7):
    #http://code.activestate.com/recipes/577124-approximately-equal/
    if tol is rel is None:
        raise TypeError('cannot specify both absolute and relative errors are None')
    tests = []
    if tol is not None: tests.append(tol)
    if rel is not None: tests.append(rel*abs(x))
    assert tests
    return abs(x - y) <= max(tests)