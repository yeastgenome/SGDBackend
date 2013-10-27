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
            'sgdid': bioent.sgdid,
            'link': bioent.link,
            'id': bioent.id
            }
    
def bioitem_to_json(bioitem):
    return {
            'display_name': bioitem.display_name, 
            'link': bioitem.link,
            'id': bioitem.id
            }
    
def chemical_to_json(chem):
    return {
            'display_name': chem.display_name, 
            'link': chem.link,
            'id': chem.id
            }
    
def source_to_json(source):
    return source.display_name
    
def go_to_json(biocon):
    biocon_json = biocon_to_json(biocon)
    biocon_json['go_id'] = biocon.go_id
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
    
def condition_to_json(condition):
    from sgdbackend_utils.cache import id_to_chem, id_to_bioent, id_to_biocon, id_to_bioitem
    if condition.class_type == 'CONDITION':
        return condition.note
    elif condition.class_type == 'CHEMICAL':
        return {'chemical': id_to_chem[condition.chemical_id],
                'amount': condition.amount,
                'note': condition.note
                }
    elif condition.class_type == 'TEMPERATURE':
        return {'temperature': condition.temperature,
                'note': condition.note
                }
    elif condition.class_type == 'BIOENTITY':
        return {
                'role': condition.role,
                'obj': id_to_bioent[condition.bioentity_id],
                'note': condition.note
                }
    elif condition.class_type == 'BIOCONCEPT':
        return {
                'role': condition.role,
                'obj': id_to_biocon[condition.bioconcept_id],
                'note': condition.note
                }
    elif condition.class_type == 'BIOITEM':
        return {
                'role': condition.role,
                'obj': id_to_bioitem[condition.bioitem_id],
                'note': condition.note
                }
    return None
    
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
            'link': url.link,
            #'category': url.category,
            #'source': url.source,
            }
    
def locustab_to_json(bioentitytab):
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
    
def disambig_to_json(disambig):
    return {
            'id': disambig.id,
            'disambig_key': disambig.disambig_key,
            'class_type': disambig.class_type,
            'subclass_type': disambig.subclass_type,
            'identifier': disambig.identifier,
           }
    
def paragraph_to_json(paragraph):
    from sgdbackend_utils import link_gene_names
    from sgdbackend_utils.cache import id_to_bioent

    references = [reference_to_json(x) for x in paragraph.references]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    bioent = id_to_bioent[paragraph.bioentity_id]
    to_ignore = {bioent['format_name'], bioent['display_name'], bioent['format_name'] + 'P', bioent['display_name'] + 'P'}
    text = link_gene_names(paragraph.text, to_ignore=to_ignore)
    return {
            'text': text,
            'references': references
           }
    