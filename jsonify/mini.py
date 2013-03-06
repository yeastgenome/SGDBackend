'''
Created on Feb 19, 2013

@author: kpaskov
'''

def bioent_mini(bioent):
    return {'name':bioent.secondary_name, 'official_name':bioent.name, 'link':'/bioent/' + bioent.name, 'description':bioent.description, 
            'bioent_type':bioent.bioent_type, 'full_name':bioent.secondary_name + ' (' + bioent.name + ')', 'id':bioent.id}
    
def reference_mini(ref):
    link_str = ref.pubmed_id
    if link_str is None:
        link_str = ref.dbxref_id
    if link_str is None:
        link_str = str(ref.id)
    link = '/reference/' + str(link_str)
    name = ref.citation[:ref.citation.find(')')]
    citation = ref.citation + " <a href='" + link + "'>pmid:" + str(ref.pubmed_id) + "</a>"
    return {'name':name, 'official_name':str(link_str), 'link':link, 'description':ref.title,
            'source': ref.source, 'status':ref.status, 'pdf_status':ref.pdf_status, 'citation': citation, 'year': str(ref.year),
            'pubmed_id': str(ref.pubmed_id), 'date_published': ref.date_published, 'date_revised':ref.date_revised, 'issue':ref.issue,
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
    basic_info['reporter'] = evidence.reporter
    basic_info['chemicals'] = [(chemical.chemical.name, chemical.chemical_amt) for chemical in evidence.phenoev_chemicals]
    basic_info['description'] = evidence.description
    return basic_info

def goevidence_mini(evidence):
    basic_info = evidence_mini(evidence)
    basic_info['go_evidence'] = evidence.go_evidence
    basic_info['annotation_type'] = evidence.annotation_type
    basic_info['source'] = evidence.source
    basic_info['date_last_reviewed'] = evidence.date_last_reviewed
    basic_info['qualifier'] = evidence.qualifier
    return basic_info
 
