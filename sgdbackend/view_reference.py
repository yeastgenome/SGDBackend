__author__ = 'kpaskov'

from sgdbackend_query.query_reference import get_abstract, get_bibentry, get_authors_for_reference, get_references_for_author, get_author
from sgdbackend_utils import link_gene_names, id_to_reference
from sgdbackend_query.query_auxiliary import get_bioentity_references

'''
-------------------------------Overview---------------------------------------
'''

def make_overview(reference_id):
    reference = dict(id_to_reference[reference_id])
    abstract = get_abstract(reference_id)
    reference['abstract'] = None if abstract is None else link_gene_names(abstract)
    reference['bibentry'] = get_bibentry(reference_id)
    reference['authors'] = get_authors_for_reference(reference_id)
    bioentity_references = get_bioentity_references(reference_id=reference_id)
    reference['counts'] = {'interaction': len([x for x in bioentity_references if x.class_type == 'PHYSINTERACTION' or x.class_type == 'GENINTERACTION']),
                            'go': len([x for x in bioentity_references if x.class_type == 'GO']),
                            'phenotype': len([x for x in bioentity_references if x.class_type == 'PHENOTYPE']),
                            'regulation': len([x for x in bioentity_references if x.class_type == 'REGULATION']),}
    return reference

'''
-------------------------------Author---------------------------------------
'''

def make_author(author_identifier):
    return get_author(author_identifier)

def make_author_references(author_id):
    references = get_references_for_author(author_id)
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references