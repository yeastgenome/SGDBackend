'''
Created on Aug 9, 2013

@author: kpaskov
'''

def bioent_to_json(bioent):
    from sgdbackend_utils.cache import get_obj
    from model_new_schema.bioentity import Bioentity

    bioent_json = {
            'id': bioent.id,
            'format_name': bioent.format_name,
            'display_name': bioent.display_name, 
            'link': bioent.link,
            'class_type': bioent.class_type,
            'sgdid': bioent.sgdid,
            'description': bioent.description
            }

    if bioent.class_type == 'LOCUS':
        bioent_json['locus_type'] = bioent.locus_type
        bioent_json['aliases'] = [x.display_name for x in bioent.aliases]
    elif bioent.class_type == 'COMPLEX':
        bioent_json['cellular_localization'] = bioent.cellular_localization
        bioent_json['go'] = minimize_json(biocon_to_json(bioent.go))
    elif bioent.class_type == 'TRANSCRIPT':
        bioent_json['locus'] = minimize_json(get_obj(Bioentity, bioent.locus_id), include_format_name=True)
    elif bioent.class_type == 'PROTEIN':
        bioent_json['locus'] = minimize_json(get_obj(Bioentity, bioent.locus_id), include_format_name=True)

    return bioent_json
    
def bioitem_to_json(bioitem):
    from model_new_schema.evelements import Source
    from sgdbackend_utils.cache import get_obj

    bioitem_json = {
            'display_name': bioitem.display_name, 
            'link': bioitem.link,
            'id': bioitem.id,
            'description': bioitem.description,
            'source': None if bioitem.source_id is None else get_obj(Source, bioitem.source_id)
            }

    if bioitem.class_type == 'DOMAIN':
        bioitem_json['interpro_id'] = bioitem.interpro_id
        bioitem_json['interpro_description'] = bioitem.interpro_description
        bioitem_json['external_link'] = bioitem.external_link

    return bioitem_json

def chemical_to_json(chem):
    return {
            'format_name': chem.format_name,
            'display_name': chem.display_name, 
            'description': chem.description,
            'chebi_id': chem.chebi_id,
            'link': chem.link,
            'id': chem.id
            }

def author_to_json(author):
    return {
        'format_name': author.format_name,
        'display_name': author.display_name,
        'link': author.link,
        'id': author.id
    }
    
def source_to_json(source):
    return source.display_name
    
def biocon_to_json(biocon):
    biocon_json = {
            'format_name': biocon.format_name,
            'display_name': biocon.display_name, 
            'description': biocon.description, 
            'class_type': biocon.class_type,
            'link': biocon.link,
            'id': biocon.id,
            'count': 0 if biocon.count is None else biocon.count.genecount,
            'child_count': 0 if biocon.count is None else biocon.count.child_gene_count
            }

    if biocon.class_type == 'GO':
        biocon_json['go_id'] = biocon.go_id
        biocon_json['go_aspect'] = biocon.go_aspect
        biocon_json['aliases'] = [x.display_name for x in biocon.aliases]
    elif biocon.class_type == 'PHENOTYPE':
        biocon_json['observable'] = biocon.observable
        biocon_json['qualifier'] = biocon.qualifier
        biocon_json['is_core'] = biocon.is_core
        biocon_json['ancestor_type'] = biocon.ancestor_type

    return biocon_json
    
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
            'description': strain.description,
            'link': strain.link,
            'id': strain.id,
            'is_alternative_reference': strain.is_alternative_reference
            }
    
def condition_to_json(condition):
    from sgdbackend_utils.cache import get_obj
    from model_new_schema.bioentity import Bioentity
    from model_new_schema.bioconcept import Bioconcept
    from model_new_schema.bioitem import Bioitem
    from model_new_schema.chemical import Chemical

    if condition.class_type == 'CONDITION':
        return condition.note
    elif condition.class_type == 'CHEMICAL':
        return {'chemical': minimize_json(get_obj(Chemical, condition.chemical_id)),
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
                'obj': minimize_json(get_obj(Bioentity, condition.bioentity_id)),
                'note': condition.note
                }
    elif condition.class_type == 'BIOCONCEPT':
        return {
                'role': condition.role,
                'obj': minimize_json(get_obj(Bioconcept, condition.bioconcept_id)),
                'note': condition.note
                }
    elif condition.class_type == 'BIOITEM':
        return {
                'role': condition.role,
                'obj': minimize_json(get_obj(Bioitem, condition.bioitem_id)),
                'note': condition.note
                }
    return None

def sequence_to_json(sequence):
    return {
        'residues': sequence.residues,
        'length': sequence.length,
        'id': sequence.id,
        'display_name': sequence.display_name,
        'format_name': sequence.format_name,
        'link': sequence.link
    }

def sequence_label_to_json(sequence_label):
    return {
        'display_name': sequence_label.display_name,
        'relative_start': sequence_label.relative_start,
        'relative_end': sequence_label.relative_end,
        'chromosomal_start': sequence_label.chromosomal_start,
        'chromosomal_end': sequence_label.chromosomal_end
    }
    
def reference_to_json(reference):
    urls = []
    if reference.pubmed_id is not None:
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
            'urls': urls,
            'journal': None if reference.journal is None else reference.journal.med_abbr,
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
            'sequence_tab': bioentitytab.sequence == 1,
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
    from model_new_schema.bioentity import Bioentity
    from sgdbackend_utils.cache import get_obj

    references = [reference_to_json(x) for x in paragraph.references]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    bioent = get_obj(Bioentity, paragraph.bioentity_id)
    to_ignore = {bioent['format_name'], bioent['display_name'], bioent['format_name'] + 'P', bioent['display_name'] + 'P'}
    text = link_gene_names(paragraph.text, to_ignore=to_ignore)
    return {
            'text': text,
            'references': references
           }
    
def evidence_to_json(evidence):
    from model_new_schema.evelements import Strain, Source, Experiment
    from model_new_schema.reference import Reference
    from sgdbackend_utils.cache import get_obj

    return {
            'id':evidence.id,
            'class_type': evidence.class_type,
            'strain': None if evidence.strain_id is None else minimize_json(get_obj(Strain, evidence.strain_id)),
            'source': None if evidence.source_id is None else get_obj(Source, evidence.source_id),
            'reference': None if evidence.reference_id is None else minimize_json(get_obj(Reference, evidence.reference_id), include_pubmed_id=True),
            'experiment': None if evidence.experiment_id is None else minimize_json(get_obj(Experiment, evidence.experiment_id)),
            'note': evidence.note}
    
def minimize_json(obj_json, include_format_name=False, include_pubmed_id=False):
    if obj_json is not None:
        min_json = {'display_name': obj_json['display_name'],
            'link': obj_json['link'],
            'id': obj_json['id']} 
        if 'class_type' in obj_json:
            min_json['class_type'] = obj_json['class_type']
        if include_format_name:
            min_json['format_name'] = obj_json['format_name']
        if include_pubmed_id:
            min_json['pubmed_id'] = obj_json['pubmed_id']
        return min_json 
    return None
