'''
Created on Aug 9, 2013

@author: kpaskov
'''

def locus_to_json(bioent):
    bioent_json = bioent_to_json(bioent)
    bioent_json['description'] = bioent.description
    bioent_json['source'] = bioent.source
    bioent_json['attribute'] = bioent.attribute
    bioent_json['name_description'] = bioent.name_description
    bioent_json['qualifier'] = bioent.qualifier
    bioent_json['alias_str'] = bioent.alias_str
    bioent_json['description'] = bioent.description
    return bioent_json

def bioent_to_json(bioent):
    return {
            'format_name': bioent.format_name,
            'bioent_type': bioent.bioent_type,
            'display_name': bioent.display_name, 
            'link': bioent.link,
            'id': bioent.id
            }
    
def biocon_to_json(biocon):
    return {
            'format_name': biocon.format_name,
            'biocon_type': biocon.biocon_type,
            'display_name': biocon.display_name, 
            'link': biocon.link,
            'id': biocon.id
            }
    
def experiment_to_json(experiment):
    return {
            'format_name': experiment.format_name,
            'display_name': experiment.display_name, 
            'link': experiment.link,
            'id': experiment.id
            }
    
def strain_to_json(strain):
    return {
            'format_name': strain.format_name,
            'display_name': strain.display_name, 
            'link': strain.link,
            'id': strain.id
            }
    
def reference_to_json(reference):
    return {
            'format_name': reference.format_name,
            'display_name': reference.display_name, 
            'link': reference.link,
            'citation': reference.citation,
            'id': reference.id,
            'year': reference.year,
            'pubmed_id': reference.pubmed_id
            }
    
def url_to_json(url):
    return {
            'url_type': url.url_type,
            'display_name': url.display_name, 
            'link': url.url,
            'category': url.category,
            'source': url.source,
            }