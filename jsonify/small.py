'''
Created on Feb 19, 2013

@author: kpaskov
'''
from jsonify.mini import bioent_mini, reference_mini

def biocon_small(biocon):
    return {'name':biocon.name, 'official_name':biocon.name, 'link':'/biocon/' + biocon.name, 'description': biocon.biocon_type + ' ' + biocon.name,
            'biocon_type':biocon.biocon_type, }    

def bioent_biocon_small(bioent_biocon):
    biocon = biocon_small(bioent_biocon.bioconcept)
    bioent = bioent_mini(bioent_biocon.bioentity)
    return {'name': bioent['name'] + unichr(8213) + biocon['name'], 'official_name':bioent_biocon.name, 'link':'/bioent_biocon/' + bioent_biocon.name, 'description': 'Relationship between bioentity ' + bioent['full_name'] + ' and bioconcept ' + biocon['name'],
            'biocon':biocon, 'bioent':bioent, 'evidence_count':bioent_biocon.evidence_count, 'evidence_desc':bioent_biocon.evidence_desc}
    
def bioent_small(bioent):
    aliases = ', '.join(bioent.alias_names)
    basic_info = bioent_mini(bioent)
    basic_info['aliases'] = aliases
    basic_info['description'] = bioent.description
    basic_info['source'] = bioent.source
    basic_info['status'] = aliases
    basic_info['qualifier'] = bioent.qualifier
    basic_info['attribute'] = bioent.attribute
    basic_info['name_description'] = bioent.short_description
    basic_info['bioent_type'] = bioent.bioent_type

    return basic_info
    
def biorel_small(biorel):
    source_bioent = bioent_mini(biorel.source_bioent)
    sink_bioent = bioent_mini(biorel.sink_bioent)
    return {'name': source_bioent['name'] + unichr(8213) + sink_bioent['name'], 'official_name':biorel.name, 'link':'/biorel/' + biorel.name, 'description': 'Interaction between ' + source_bioent['full_name'] + ' and ' + sink_bioent['full_name'],
            'source':source_bioent, 'sink':sink_bioent, 
            'evidence_count':biorel.evidence_count, 'physical_evidence_count':biorel.physical_evidence_count, 'genetic_evidence_count':biorel.genetic_evidence_count} 

def evidence_small(evidence):
    if evidence.reference is not None:
        reference = reference_mini(evidence.reference)
    else:
        reference = None
    return {'name':'Evidence ' + str(evidence.id), 'official_name': str(evidence.id), 'link':'/evidence/' + str(evidence.id), 'description': 'Evidence',
            'experiment_type':evidence.experiment_type, 'reference':reference, 'strain':evidence.strain_id}

def allele_small(allele):
    return {'name': allele.name, 'official_name':allele.name, 'link':str('/allele/' + str(allele.name)), 'description': 'Allele',
            'more_info':allele.description}
    
def interevidence_small(evidence):
    basic_info = evidence_small(evidence)

    basic_info['annotation_type'] = evidence.annotation_type
    basic_info['modification'] = evidence.modification
    basic_info['direction'] = evidence.direction
    basic_info['interaction_type'] = evidence.interaction_type
    basic_info['observable'] = evidence.observable
    basic_info['qualifier'] = evidence.qualifier
    return basic_info

def phenoevidence_small(evidence): 
    basic_info = evidence_small(evidence)
    basic_info['mutant'] = evidence.mutant_type
    basic_info['allele'] = evidence.mutant_allele
    basic_info['source'] = evidence.source
    basic_info['qualifier'] = evidence.qualifier
    basic_info['comment'] = evidence.experiment_comment
    return basic_info

def reference_small(ref):
    basic_info = reference_mini(ref)

    if ref.book_id is not None:
        basic_info['book'] = ref.book.title
    else:
        basic_info['book'] = None
    if ref.journal_id is not None:
        basic_info['journal'] = ref.journal.full_name
    else:
        basic_info['journal'] = None
    basic_info['abstract'] = ref.abstract
    return basic_info