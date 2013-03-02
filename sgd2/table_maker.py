'''
Created on Feb 20, 2013

@author: kpaskov
'''
    

def create_table(objects, metadata):
    table = []
    for obj in objects:
        object_info = []
        for metadatum in metadata:
            output = str(obj[metadatum['field']])
            if 'link' in metadatum:
                value = obj
                for key in metadatum['link']:
                    value = value[key]
                output = entry_with_link(output, str(value))
            if 'note' in metadatum:
                value = obj
                for key in metadatum['note']:
                    value = value[key]
                output = entry_with_note(output, str(value))
            object_info.append(output)
        table.append(object_info) 
    return {'aaData':table}
    
def create_note(qualifiers):
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
    
        

def create_bioent_biocon_table_for_bioent(evidences):
    name_to_bioent_biocons = {}
    bb_name_to_null_qualifiers = {}
    bb_name_to_overexpression_qualifiers = {}
    bb_name_to_conditional_qualifiers = {}
    
    for evidence in evidences:
        bb = evidence['bioent_biocon']
        bb_name = bb['name']
        name_to_bioent_biocons[bb_name] = bb
        if evidence['mutant'] == 'null':
            if bb_name in bb_name_to_null_qualifiers:
                bb_name_to_null_qualifiers[bb_name].append(evidence['qualifier'])
            else:
                bb_name_to_null_qualifiers[bb_name] = [evidence['qualifier']]
        if evidence['mutant'] == 'overexpression':
            if bb_name in bb_name_to_overexpression_qualifiers:
                bb_name_to_overexpression_qualifiers[bb_name].append(evidence['qualifier'])
            else:
                bb_name_to_overexpression_qualifiers[bb_name] = [evidence['qualifier']]
        if evidence['mutant'] == 'conditional':
            if bb_name in bb_name_to_conditional_qualifiers:
                bb_name_to_conditional_qualifiers[bb_name].append(evidence['qualifier'])
            else:
                bb_name_to_conditional_qualifiers[bb_name] = [evidence['qualifier']]
                
    
        
    table = []
    for bioent_biocon in name_to_bioent_biocons.values():
        bb_name = bioent_biocon['name']
        bioent_biocon_entry = entry_with_link('&#151;' + bioent_biocon['biocon']['name'], bioent_biocon['link'])
        null_entry = '0'
        overex_entry = '0'
        cond_entry = '0'
        all_quals = []
        if bb_name in bb_name_to_null_qualifiers:
            quals = bb_name_to_null_qualifiers[bb_name]
            null_entry = entry_with_note(str(len(quals)), create_note(quals))
            all_quals.extend(quals)
        if bb_name in bb_name_to_overexpression_qualifiers:
            quals = bb_name_to_overexpression_qualifiers[bb_name]
            overex_entry = entry_with_note(str(len(quals)), create_note(quals))
            all_quals.extend(quals)
        if bb_name in bb_name_to_conditional_qualifiers:
            quals = bb_name_to_conditional_qualifiers[bb_name]
            cond_entry = entry_with_note(str(len(quals)), create_note(quals))
            all_quals.extend(quals)
        total_entry = entry_with_note(entry_with_link(str(len(all_quals)), bioent_biocon['link']), create_note(all_quals))
            
        table.append([bioent_biocon_entry, null_entry, overex_entry, cond_entry, total_entry])
    return {'aaData':table}

def get_biorel_name(biorel, bioent_name):
    source_or_sink = None
    if biorel['source']['official_name'] == bioent_name:
        source_or_sink = 'sink'
    else:
        source_or_sink = 'source'
    return '&#151;' + biorel[source_or_sink]['name']

def create_biorel_table_for_bioent(bioent_name, biorels):
    table = []
    for biorel in biorels:     
        biorel_entry = entry_with_link(get_biorel_name(biorel, bioent_name), biorel['link'])
        total_entry = entry_with_link(str(biorel['evidence_count']), biorel['link'])

        table.append([biorel_entry, str(biorel['genetic_evidence_count']), str(biorel['physical_evidence_count']), total_entry])
    return {'aaData':table}

def create_bioent_biocon_table_for_biocon(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_biocon_entry = entry_with_link('&#151;' + bioent_biocon['bioent']['name'], bioent_biocon['link'])
        
        evidence_desc = bioent_biocon['evidence_desc']
        if evidence_desc:
            evidence_entry = entry_with_note(str(bioent_biocon['evidence_count']), '(' + evidence_desc + ')')
        else:
            evidence_entry = str(bioent_biocon['evidence_count'])
        table.append([bioent_biocon_entry, evidence_entry])
    return {'aaData':table}

def create_evidence_table_for_bioent_biocon(evidences):
    table = []
    for evidence in evidences:
        bioent_biocon_entry = entry_with_link('&#151;' + evidence['bioent_biocon']['biocon']['name'], evidence['bioent_biocon']['link'])
        if evidence['allele']:
            allele_entry = entry_with_link(evidence['allele']['name'], evidence['allele']['link'])
        else:
            allele_entry = None
        reference_entry = entry_with_link(evidence['reference']['name'], evidence['reference']['link'])
        
        table.append([bioent_biocon_entry, evidence['qualifier'], evidence['experiment_type'], evidence['mutant'], allele_entry, evidence['strain'], reference_entry])
    return {'aaData':table}

def create_phenotype_table_for_reference(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_biocon_entry = entry_with_link(bioent_biocon['name'], bioent_biocon['link'])
        biocon_entry = entry_with_link(bioent_biocon['biocon']['name'], bioent_biocon['biocon']['link'])
        bioent_entry = entry_with_link(bioent_biocon['bioent']['name'], bioent_biocon['bioent']['link'])
        table.append([bioent_biocon_entry, biocon_entry, bioent_entry])
    return {'aaData':table}

def create_interaction_table_for_reference(biorels):
    table = []
    for biorel in biorels:
        biorel_entry = entry_with_link(biorel['name'], biorel['link'])
        endpoint1_entry = entry_with_link(biorel['source']['name'], biorel['source']['link'])
        endpoint2_entry = entry_with_link(biorel['sink']['name'], biorel['sink']['link'])
        table.append([biorel_entry, endpoint1_entry, endpoint2_entry])
    return {'aaData':table}

def reverse_direction(direction):
    if direction == 'bait-hit':
        return 'hit-bait'
    else:
        return 'bait-hit'

def create_genetic_evidence_table_for_interaction(evidences, bioent_name):
    table = []
    for evidence in evidences:
        reference_entry = entry_with_link(evidence['reference']['name'], evidence['reference']['link'])
        phenotype = ''
        if evidence['qualifier'] is not None:
            phenotype = evidence['qualifier'] + ' ' + evidence['observable']
            
        if bioent_name is None:
            biorel_entry = None
            direction = evidence['direction']
        else:
            biorel = evidence['biorel']
            biorel_entry = entry_with_link(get_biorel_name(biorel, bioent_name), biorel['link'])

            if biorel['source']['official_name'] == bioent_name:
                direction = evidence['direction']
            else:
                direction = reverse_direction(evidence['direction'])
        table.append([biorel_entry, evidence['experiment_type'], evidence['annotation_type'], direction, phenotype, reference_entry])
    return {'aaData':table}

def create_physical_evidence_table_for_interaction(evidences, bioent_name):
    table = []
    for evidence in evidences:
        reference_entry = entry_with_link(evidence['reference']['name'], evidence['reference']['link'])
        
        if bioent_name is None:
            biorel_entry = None
            direction = evidence['direction']
        else:
            biorel = evidence['biorel']
            biorel_entry = entry_with_link(get_biorel_name(biorel, bioent_name), biorel['link'])

            if biorel['source']['official_name'] == bioent_name:
                direction = evidence['direction']
            else:
                direction = reverse_direction(evidence['direction'])
        table.append([biorel_entry, evidence['experiment_type'], evidence['annotation_type'], direction, evidence['modification'], reference_entry])
    return {'aaData':table}

def entry_with_link(entry_name, link):
    return"<a href='" + link + "'>" + entry_name + "</a>"

def entry_with_note(entry_name, note):
    return "<span>" + entry_name + "</span><span class='muted' style='float:right'>" + note + "</span>"
