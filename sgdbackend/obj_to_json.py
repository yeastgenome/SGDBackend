'''
Created on Aug 9, 2013

@author: kpaskov
'''

def locus_to_json(bioent):
    bioent_json = bioent_to_json(bioent)
    bioent_json['description'] = bioent.description
    #bioent_json['source'] = bioent.source
    #bioent_json['attribute'] = bioent.attribute
    #bioent_json['name_description'] = bioent.name_description
    #bioent_json['alias_str'] = bioent.alias_str
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
    #biocon_json['aliases'] = biocon.aliases
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
    urls = []
    urls.append({'display_name': 'PubMed', 'link': 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(reference.pubmed_id)})

    if reference.doi is not None:
        urls.append({'display_name': 'Full-Text', 'link': 'http://dx.doi.org/' + reference.doi})
    if reference.pubmed_central_id is not None:
        urls.append({'display_name': 'PMC', 'link': 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(reference.pubmed_central_id)})

    return {
            'format_name': reference.format_name,
            'display_name': reference.display_name, 
            'link': reference.link,
            'citation': reference.citation,
            'id': reference.id,
            'year': reference.year,
            'pubmed_id': reference.pubmed_id,
            'urls': urls
            }
    
def url_to_json(url):
    return {
            #'url_type': url.class_type,
            'display_name': url.display_name, 
            'link': url.url,
            #'category': url.category,
            #'source': url.source,
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
    
def bioentitytab_to_json(bioentitytab):
    return {
            'bioentity_id': bioentitytab.id,
            'summary_tab': bioentitytab.summary == 1,
            'history_tab': bioentitytab.history == 1,
            'literature_tab': bioentitytab.literature == 1,
            'go_tab': bioentitytab.go == 1,
            'phenotype_tab': bioentitytab.phenotype == 1,
            'interaction_tab': bioentitytab.interactions == 1,
            'expression_tab': bioentitytab.expression == 1,
            'regulation_tab': bioentitytab.regulation == 1,
            'protein_tab': bioentitytab.protein == 1,
            'wiki_tab': bioentitytab.wiki == 1
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
    