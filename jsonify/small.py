'''
Created on Feb 19, 2013

@author: kpaskov
'''
from jsonify.add_hyperlinks import add_gene_hyperlinks
from jsonify.mini import bioent_mini, reference_mini, phenoevidence_mini, \
    interevidence_mini

def biocon_small(biocon):
    return {'name':biocon.name, 'official_name':biocon.name, 'link':'/biocon/' + biocon.name, 'description': biocon.biocon_type + ' ' + biocon.name,
            'biocon_type':biocon.biocon_type, }    

def bioent_biocon_small(bioent_biocon):
    biocon = biocon_small(bioent_biocon.bioconcept)
    bioent = bioent_mini(bioent_biocon.bioentity)
    return {'name': bioent['name'] + unichr(8213) + biocon['name'], 'official_name':bioent_biocon.name, 'link':'/bioent_biocon/' + bioent_biocon.official_name, 'description': 'Relationship between bioentity ' + bioent['full_name'] + ' and bioconcept ' + biocon['name'],
            'biocon':biocon, 'bioent':bioent, 'evidence_count':bioent_biocon.evidence_count, 'evidence_desc':bioent_biocon.evidence_desc, 'all':0}
    
def bioent_small(bioent):
    aliases = ', '.join(bioent.alias_names)
    basic_info = bioent_mini(bioent)
    basic_info['aliases'] = aliases
    print bioent.description
    basic_info['description'] = add_gene_hyperlinks(bioent.description)
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
            'source':source_bioent, 'sink':sink_bioent, 'all':0,
            'evidence_count':biorel.evidence_count, 'physical_evidence_count':biorel.physical_evidence_count, 'genetic_evidence_count':biorel.genetic_evidence_count} 
    
def all_biorel_small(bioent):
    bioent_basic_info = bioent_small(bioent)
    return {'name':bioent_basic_info['name'] + unichr(8213) + 'All Genes', 'description':'All interactions between ' + bioent_basic_info['name'] + ' and other genes.', 
                  'source': bioent_basic_info, 'sink': None, 'link': '/biorel/' + bioent_basic_info['official_name'], 'all':1}

def all_bioent_biocon_small(bioent):
    bioent_basic_info = bioent_small(bioent)
    return {'name':bioent_basic_info['name'] + unichr(8213) + 'All Phenotypes', 'description':'All phenotypes for ' + bioent_basic_info['name'] + '.', 
                  'bioent': bioent_basic_info, 'biocon': None, 'link': '/bioent_biocon/' + bioent_basic_info['official_name'], 'all':1}

def allele_small(allele):
    return {'name': allele.name, 'official_name':allele.name, 'link':str('/allele/' + str(allele.name)), 'description': 'Allele',
            'more_info':allele.description}

def phenoevidence_small(evidence):
    basic_info = phenoevidence_mini(evidence)
    if evidence.mutant_allele is not None:
        basic_info['allele'] = allele_small(evidence.mutant_allele)
    else:
        basic_info['allele'] = None
    basic_info['biorel'] = None
    return basic_info

def phenoevidence_mid(evidence):
    basic_info = phenoevidence_small(evidence)
    basic_info['bioent_biocon'] = bioent_biocon_small(evidence.bioent_biocon)
    return basic_info

def interevidence_small(evidence):
    basic_info = interevidence_mini(evidence)
    basic_info['bioent_biocon'] = None
    basic_info['biorel'] = biorel_small(evidence.biorel)
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
    if ref.abst is not None:
        basic_info['abstract'] = add_gene_hyperlinks(ref.abstract)
    else:
        basic_info['abstract'] = None
    return basic_info