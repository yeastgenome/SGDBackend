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
    bioent_json['alias_str'] = bioent.alias_str
    bioent_json['description'] = bioent.description
    return bioent_json

def bioent_to_json(bioent):
    return {
            'format_name': bioent.format_name,
            'bioent_type': bioent.class_type,
            'display_name': bioent.display_name, 
            'link': bioent.link,
            'id': bioent.id
            }
    
def go_to_json(biocon):
    biocon_json = biocon_to_json(biocon)
    biocon_json['go_go_id'] = biocon.go_go_id
    biocon_json['go_aspect'] = biocon.go_aspect
    biocon_json['aliases'] = biocon.aliases
    return biocon_json
    
def biocon_to_json(biocon):
    return {
            'format_name': biocon.format_name,
            'biocon_type': biocon.class_type,
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
    
def reference_to_json_full(reference):
    reference_json = reference_to_json(reference)
    
    reference_json['status'] = reference.status
    reference_json['date_published'] = reference.date_published
    reference_json['title'] = reference.title
    reference_json['abstract'] = reference.abstract
    reference_json['authors'] = reference.author_list
    reference_json['reftypes'] = reference.reftype_list
    reference_json['source'] = reference.source
    reference_json['date_revised'] = reference.date_revised
    reference_json['issue'] = reference.issue
    reference_json['page'] = reference.page
    reference_json['volume'] = reference.volume
    
    
    if reference.journal is not None:
        reference_json['issn'] = reference.journal.issn
        reference_json['journal_name'] = reference.journal.full_name
        reference_json['journal_name_abbrev'] = reference.journal.abbreviation
    else:
        reference_json['issn'] = None
        reference_json['journal_name'] = None
        reference_json['journal_name_abbrev'] = None
        
    if reference.book is not None:
        reference_json['publisher_location'] = reference.book.publisher_location
        reference_json['book_title'] = reference.book.title
        reference_json['volume_title'] = reference.book.volume_title
        reference_json['isbn'] = reference.book.isbn
    else:
        reference_json['publisher_location'] = None
        reference_json['book_title'] = None
        reference_json['volume_title'] = None
        reference_json['isbn'] = None
        
    return reference_json
    
def url_to_json(url):
    return {
            'url_type': url.class_type,
            'display_name': url.display_name, 
            'link': url.url,
            'category': url.category,
            'source': url.source,
            }
    
def domain_to_json(domain):
    return {
            'source': domain.source,
            'display_name': domain.display_name,
            'format_name': domain.format_name,
            'description': domain.description,
            'interpro_id': domain.interpro_id,
            'interpro_description': domain.interpro_description,
            'link': domain.link
           }
    
def paragraph_to_json(paragraph):
    from sgdbackend.utils import link_gene_names
    from sgdbackend.cache import get_cached_bioent

    references = [reference_to_json(x) for x in paragraph.references]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    bioent = get_cached_bioent(paragraph.bioentity_id)
    to_ignore = {bioent['format_name'], bioent['display_name'], bioent['format_name'] + 'P', bioent['display_name'] + 'P'}
    text = link_gene_names(paragraph.text, to_ignore=to_ignore)
    return {
            'text': text,
            'references': references
           }
    