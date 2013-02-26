'''
Created on Feb 20, 2013

@author: kpaskov
'''
    

def create_bioent_biocon_table_for_bioent(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_biocon_entry = entry_with_link(bioent_biocon['name'], bioent_biocon['link'])
        biocon_entry = entry_with_link(bioent_biocon['biocon']['name'], bioent_biocon['biocon']['link'])
        
        evidence_desc = bioent_biocon['evidence_desc']
        if evidence_desc:
            evidence_entry = entry_with_note(str(bioent_biocon['evidence_count']), '(' + evidence_desc + ')')
        else:
            evidence_entry = str(bioent_biocon['evidence_count'])
            
        table.append([bioent_biocon_entry, biocon_entry, evidence_entry])
    return {'aaData':table}

def create_biorel_table_for_bioent(bioent_name, biorels):
    table = []
    for biorel in biorels:
        source_or_sink = None
        if biorel['source']['official_name'] == bioent_name:
            source_or_sink = 'sink'
        else:
            source_or_sink = 'source'
            
        biorel_entry = entry_with_link(biorel['name'], biorel['link'])
        bioent_entry = entry_with_link(biorel[source_or_sink]['name'], biorel[source_or_sink]['link'])
        table.append([biorel_entry, bioent_entry, str(biorel['genetic_evidence_count']), str(biorel['physical_evidence_count']), str(biorel['evidence_count'])])
    return {'aaData':table}

def create_biorel_table_for_bioent2(bioent_name, biorels):
    table = []
    for biorel in biorels:
        source_or_sink = None
        if biorel['source']['official_name'] == bioent_name:
            source_or_sink = 'sink'
        else:
            source_or_sink = 'source'
            
        biorel_entry = entry_with_link("O--O", biorel['link'])
        bioent_entry = entry_with_link(biorel[source_or_sink]['name'], biorel[source_or_sink]['link'])
        table.append([biorel_entry, bioent_entry, str(biorel['genetic_evidence_count']), str(biorel['physical_evidence_count']), str(biorel['evidence_count'])])
    return {'aaData':table}

def create_biorel_table_for_bioent3(bioent_name, biorels):
    table = []
    for biorel in biorels:
        source_or_sink = None
        if biorel['source']['official_name'] == bioent_name:
            source_or_sink = 'sink'
        else:
            source_or_sink = 'source'
            
        biorel_entry = entry_with_link("O--O", biorel['link'])
        bioent_entry = entry_with_link(biorel[source_or_sink]['name'], biorel[source_or_sink]['link'])
        genetic_entry = entry_with_link(str(biorel['genetic_evidence_count']), biorel['link'] + '#genetic_evidence')
        physical_entry = entry_with_link(str(biorel['physical_evidence_count']), biorel['link'] + '#physical_evidence')
        total_entry = entry_with_link(str(biorel['evidence_count']), biorel['link'])

        table.append([biorel_entry, bioent_entry, genetic_entry, physical_entry, total_entry])
    return {'aaData':table}

def create_bioent_biocon_table_for_biocon(bioent_biocons):
    table = []
    for bioent_biocon in bioent_biocons:
        bioent_biocon_entry = entry_with_link(bioent_biocon['name'], bioent_biocon['link'])
        bioent_entry = entry_with_link(bioent_biocon['bioent']['name'], bioent_biocon['bioent']['link'])
        
        evidence_desc = bioent_biocon['evidence_desc']
        if evidence_desc:
            evidence_entry = entry_with_note(str(bioent_biocon['evidence_count']), '(' + evidence_desc + ')')
        else:
            evidence_entry = str(bioent_biocon['evidence_count'])
        table.append([bioent_biocon_entry, bioent_entry, evidence_entry])
    return {'aaData':table}

def create_evidence_table_for_bioent_biocon(evidences):
    table = []
    for evidence in evidences:
        evidence_entry = entry_with_link(evidence['name'], evidence['link'])
        if evidence['allele']:
            mutant_entry = entry_with_note(evidence['mutant'], entry_with_link('(' + evidence['allele']['name'] + ')', evidence['allele']['link']))
        else:
            mutant_entry = evidence['mutant']
        reference_entry = entry_with_link(evidence['reference']['name'], evidence['reference']['link'])
        
        table.append([evidence_entry, evidence['qualifier'], evidence['experiment_type'], mutant_entry, evidence['strain'], reference_entry])
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

def create_genetic_evidence_table_for_interaction(evidences):
    table = []
    for evidence in evidences:
        evidence_entry = entry_with_link(evidence['name'], evidence['link'])
        reference_entry = entry_with_link(evidence['reference']['name'], evidence['reference']['link'])
        phenotype = ''
        if evidence['qualifier'] is not None:
            phenotype = evidence['qualifier'] + ' ' + evidence['observable']
        table.append([evidence_entry, evidence['experiment_type'], evidence['annotation_type'], evidence['direction'], phenotype, reference_entry])
    return {'aaData':table}

def create_physical_evidence_table_for_interaction(evidences):
    table = []
    for evidence in evidences:
        evidence_entry = entry_with_link(evidence['name'], evidence['link'])
        reference_entry = entry_with_link(evidence['reference']['name'], evidence['reference']['link'])
        table.append([evidence_entry, evidence['experiment_type'], evidence['annotation_type'], evidence['direction'], evidence['modification'], reference_entry])
    return {'aaData':table}

def entry_with_link(entry_name, link):
    return"<a href='" + link + "'>" + entry_name + "</a>"

def entry_with_note(entry_name, note):
    return "<span>" + entry_name + "</span><span class='muted' style='float:right'>" + note + "</span>"
