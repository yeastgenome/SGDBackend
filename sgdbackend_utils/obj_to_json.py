'''
Created on Aug 9, 2013

@author: kpaskov
'''
def locus_to_json(bioent):
    bioent_json = bioent_to_json(bioent)
    bioent_json['description'] = bioent.description
    return bioent_json

def bioent_to_json(bioent):
    return {
            'id': bioent.id,
            'format_name': bioent.format_name,
            'display_name': bioent.display_name, 
            'link': bioent.link,
            'class_type': bioent.class_type,
            'sgdid': bioent.sgdid,
            }
    
def bioitem_to_json(bioitem):
    return {
            'display_name': bioitem.display_name, 
            'link': bioitem.link,
            'id': bioitem.id,
            'description': bioitem.description,
            }
    
def chemical_to_json(chem):
    return {
            'format_name': chem.format_name,
            'display_name': chem.display_name, 
            'description': chem.description,
            'chebi_id': chem.chebi_id,
            'link': chem.link,
            'id': chem.id
            }
    
def source_to_json(source):
    return source.display_name
    
def go_to_json(biocon):
    biocon_json = biocon_to_json(biocon)
    biocon_json['go_id'] = biocon.go_id
    biocon_json['go_aspect'] = biocon.go_aspect
    return biocon_json

def phenotype_to_json(biocon):
    biocon_json = biocon_to_json(biocon)
    biocon_json['observable'] = biocon.observable
    biocon_json['qualifier'] = biocon.qualifier
    biocon_json['mutant_type'] = biocon.mutant_type
    biocon_json['is_core'] = biocon.is_core
    biocon_json['ancestor_type'] = biocon.ancestor_type
    return biocon_json
    
def biocon_to_json(biocon):
    return {
            'format_name': biocon.format_name,
            'display_name': biocon.display_name, 
            'description': biocon.description, 
            'class_type': biocon.class_type,
            'link': biocon.link,
            'id': biocon.id,
            'count': 0 if biocon.count is None else biocon.count.genecount
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
            'id': bioentitytab.id,
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
    
def evidence_to_json(evidence):
    from sgdbackend_utils.cache import id_to_strain, id_to_source, id_to_reference, id_to_experiment
    return {
            'id':evidence.id,
            'class_type': evidence.class_type,
            'strain': None if evidence.strain_id is None else minimize_json(id_to_strain[evidence.strain_id]),
            'source': None if evidence.source_id is None else id_to_source[evidence.source_id],
            'reference': None if evidence.reference_id is None else minimize_json(id_to_reference[evidence.reference_id]),
            'experiment': None if evidence.experiment_id is None else minimize_json(id_to_experiment[evidence.experiment_id]),
            'note': evidence.note}
    
def minimize_json(obj_json, include_format_name=False):
    if obj_json is not None:
        min_json = {'display_name': obj_json['display_name'],
            'link': obj_json['link'],
            'id': obj_json['id']} 
        if 'class_type' in obj_json:
            min_json['class_type'] = obj_json['class_type']
        if include_format_name:
            min_json['format_name'] = obj_json['format_name']
        return min_json 
    return None
