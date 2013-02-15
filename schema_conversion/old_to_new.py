'''
Created on Feb 4, 2013

@author: kpaskov
'''

def feature_to_bioent(feature):
    from model_new_schema.bioentity import Bioentity
    qualifier = None
    attribute = None
    short_description = None
    headline = None
    description = None
    genetic_position = None
    
    ann = feature.annotation
    if ann is not None:
        qualifier = ann.qualifier
        attribute = ann.attribute
        short_description = ann.name_description
        headline = ann.headline
        description = ann.description
        genetic_position = ann.genetic_position
        
    bioent = Bioentity(feature.name, feature_type_to_bioent_type(feature.type), feature.dbxref_id, feature.source, feature.status, feature.gene_name, 
                       qualifier, attribute, short_description, headline, description, genetic_position,
                       bioent_id=feature.id, date_created=feature.date_created, created_by=feature.created_by)
    return bioent

def feature_type_to_bioent_type(feature_type):
    bioent_type = feature_type.upper()
    bioent_type.replace (" ", "_")
    return bioent_type

def reference_to_reference(reference):
    from model_new_schema.reference import Reference
    
    new_ref = Reference(reference.pubmed_id, reference_id=reference.id, source=reference.source, status=reference.status, pdf_status=reference.pdf_status, 
                        dbxref_id=reference.dbxref_id, citation=reference.citation, year=reference.year, date_published=reference.date_published,
                        date_revised=reference.date_revised, issue=reference.issue, page=reference.page, volume=reference.volume, title=reference.title,
                        journal_id=reference.journal_id, book_id=reference.book_id, date_created=reference.date_created, created_by=reference.date_created)
    return new_ref

def book_to_book(book):
    from model_new_schema.reference import Book
    
    new_book = Book(book.title, book.volume_title, book.isbn, book.total_pages, book.publisher, book.publisher_location, 
                    book_id=book.id, date_created=book.date_created, created_by=book.created_by)
    return new_book

def journal_to_journal(journal):
    from model_new_schema.reference import Journal
    new_journal = Journal(journal.abbreviation, journal_id=journal.id, full_name=journal.full_name, issn=journal.issn, essn=journal.essn,
                          created_by=journal.created_by, date_created = journal.date_created)
    return new_journal

def author_to_author(author):
    from model_new_schema.reference import Author
    
    new_author = Author(author.name, author_id=author.id, created_by=author.created_by, date_created=author.date_created)
    return new_author

def abstract_to_abstract(abstract):
    from model_new_schema.reference import Abstract
    
    new_abstract = Abstract(abstract.text, abstract.reference_id)
    return new_abstract

def reftype_to_reftype(reftype):
    from model_new_schema.reference import Reftype
    
    new_reftype = Reftype(reftype.name, reftype_id=reftype.id, source=reftype.source, created_by=reftype.created_by, date_created=reftype.date_created)
    return new_reftype

def interaction_to_biorel(interaction):
    from model_new_schema.biorelation import Biorelation
    
    bait_id = interaction.features['Bait'].id
    hit_id = interaction.features['Hit'].id
    if bait_id < hit_id:
        new_biorel = Biorelation('INTERACTION', bait_id, hit_id, biorel_id=interaction.id, created_by=interaction.created_by, date_created=interaction.date_created)
    else:
        new_biorel = Biorelation('INTERACTION', hit_id, bait_id, biorel_id=interaction.id, created_by=interaction.created_by, date_created=interaction.date_created)
    return new_biorel
        
def experiment_property_to_phenoevidence_property(experiment_property):
    from model_new_schema.evidence import PhenoevidenceProperty
    
    new_phenoevidence_property = PhenoevidenceProperty(experiment_property.type, experiment_property.value, experiment_property.description, evidence_id=experiment_property.id)
    return new_phenoevidence_property
