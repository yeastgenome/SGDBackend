'''
Created on Feb 19, 2013

@author: kpaskov
'''

def bioent_mini(bioent):
    return {'name':bioent.secondary_name, 'official_name':bioent.name, 'link':'/bioent/' + bioent.name, 'description':bioent.description, 
            'bioent_type':bioent.bioent_type, 'full_name':bioent.secondary_name + ' (' + bioent.name + ')', 'id':bioent.id}
    
def reference_mini(ref):
    pubmed_str = str(ref.pubmed_id)
    link = '/reference/' + pubmed_str
    citation = "<a href='" + link + "'>" + ref.citation[:len(ref.name)] + "</a>" + ref.citation[len(ref.name):]
    return {'name':ref.name, 'official_name':pubmed_str, 'link':link, 'description':ref.title,
            'source': ref.source, 'status':ref.status, 'pdf_status':ref.pdf_status, 'citation': citation, 'year': str(ref.year),
            'pubmed_id': pubmed_str, 'date_published': ref.date_published, 'date_revised':ref.date_revised, 'issue':ref.issue,
            'page':ref.page, 'volume':ref.volume, 'title':ref.title, 'doi':ref.doi, 'name':ref.name} 

def evidence_mini(evidence):
    if evidence.reference is not None:
        reference = reference_mini(evidence.reference)
    else:
        reference = None
    return {'name':'Evidence ' + str(evidence.id), 'official_name': str(evidence.id), 'link':'/evidence/' + str(evidence.id), 'description': 'Evidence',
            'experiment_type':evidence.experiment_type, 'reference':reference, 'strain':evidence.strain_id}

def interevidence_mini(evidence):
    basic_info = evidence_mini(evidence)

    basic_info['annotation_type'] = evidence.annotation_type
    basic_info['modification'] = evidence.modification
    basic_info['direction'] = evidence.direction
    basic_info['interaction_type'] = evidence.interaction_type
    basic_info['observable'] = evidence.observable
    basic_info['qualifier'] = evidence.qualifier
    return basic_info

def phenoevidence_mini(evidence): 
    basic_info = evidence_mini(evidence)
    basic_info['mutant'] = evidence.mutant_type
    basic_info['source'] = evidence.source
    basic_info['qualifier'] = evidence.qualifier
    basic_info['comment'] = evidence.experiment_comment
    return basic_info