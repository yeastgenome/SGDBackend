'''
Created on Feb 19, 2013

@author: kpaskov
'''

def bioent_mini(bioent):
    return {'name':bioent.secondary_name, 'official_name':bioent.name, 'link':'/bioent/' + bioent.name, 'description':bioent.description, 
            'bioent_type':bioent.bioent_type, 'full_name':bioent.secondary_name + ' (' + bioent.name + ')'}
    
def reference_mini(ref):
    pubmed_str = str(ref.pubmed_id)
    return {'name':ref.name, 'official_name':pubmed_str, 'link':'/reference/' + pubmed_str, 'description':ref.title,
            'source': ref.source, 'status':ref.status, 'pdf_status':ref.pdf_status, 'citation': ref.citation, 'year': str(ref.year),
            'pubmed_id': pubmed_str, 'date_published': ref.date_published, 'date_revised':ref.date_revised, 'issue':ref.issue,
            'page':ref.page, 'volume':ref.volume, 'title':ref.title, 'doi':ref.doi, 'name':ref.name} 
