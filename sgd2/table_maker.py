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
    

    
        


def get_biorel_name(biorel, bioent_name):
    source_or_sink = None
    if biorel['source']['official_name'] == bioent_name:
        source_or_sink = 'sink'
    else:
        source_or_sink = 'source'
    return '&#151;' + biorel[source_or_sink]['name']





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




def create_go_table_for_bioent_biocon(evidences):
    table = []
    for evidence in evidences:
        reference_entry = evidence['reference']['name'] + ' <small>pmid:' + entry_with_link(str(evidence['reference']['pubmed_id']), evidence['reference']['link']) + '</small>'
        table.append([evidence['go_evidence'], evidence['annotation_type'], evidence['source'], evidence['qualifier'], evidence['date_last_reviewed'], reference_entry])
    return {'aaData':table}   

def entry_with_link(entry_name, link):
    return"<a href='" + link + "'>" + entry_name + "</a>"

def entry_with_note(entry_name, note):
    return "<span>" + entry_name + "</span><span class='muted' style='float:right'>" + note + "</span>"
