'''
Created on Jul 9, 2013

@author: kpaskov
'''
from model_new_schema.auxiliary import BioentityReference
from model_new_schema.bioentity import Bioentity
from model_new_schema.misc import Url
from model_new_schema.reference import Reference, Author, AuthorReference, \
    Bibentry
from sgdbackend_query import session
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func

#Used for Reference page.
def get_reference(reference_name, print_query=False):
    '''
    get_reference('7635312', print_query=True)
    
    SELECT sprout.reference.reference_id AS sprout_reference_reference_id, sprout.reference.citation AS sprout_reference_citation, sprout.reference.fulltext_url AS sprout_reference_fulltext_url, sprout.reference.source AS sprout_reference_source, sprout.reference.status AS sprout_reference_status, sprout.reference.pdf_status AS sprout_reference_pdf_status, sprout.reference.dbxref_id AS sprout_reference_dbxref_id, sprout.reference.year AS sprout_reference_year, sprout.reference.pubmed_id AS sprout_reference_pubmed_id, sprout.reference.date_published AS sprout_reference_date_pu_1, sprout.reference.date_revised AS sprout_reference_date_revised, sprout.reference.issue AS sprout_reference_issue, sprout.reference.page AS sprout_reference_page, sprout.reference.volume AS sprout_reference_volume, sprout.reference.title AS sprout_reference_title, sprout.reference.journal_id AS sprout_reference_journal_id, sprout.reference.book_id AS sprout_reference_book_id, sprout.reference.doi AS sprout_reference_doi, sprout.reference.created_by AS sprout_reference_created_by, sprout.reference.date_created AS sprout_reference_date_created, abstract_1.abstract AS abstract_1_abstract, abstract_1.reference_id AS abstract_1_reference_id, author_reference_1.author_reference_id AS author_reference_1_autho_2, author_reference_1.author_order AS author_reference_1_autho_3, author_reference_1.author_type AS author_reference_1_author_type, author_1.author_id AS author_1_author_id, author_1.author_name AS author_1_author_name, author_1.created_by AS author_1_created_by, author_1.date_created AS author_1_date_created, author_reference_1.author_id AS author_reference_1_author_id, author_reference_1.reference_id AS author_reference_1_refer_4 
    FROM sprout.reference LEFT OUTER JOIN sprout.abstract abstract_1 ON sprout.reference.reference_id = abstract_1.reference_id LEFT OUTER JOIN sprout.author_reference author_reference_1 ON sprout.reference.reference_id = author_reference_1.reference_id LEFT OUTER JOIN sprout.author author_1 ON author_1.author_id = author_reference_1.author_id 
    WHERE sprout.reference.pubmed_id = :pubmed_id_1
    '''
    query = session.query(Reference).filter(Reference.format_name==reference_name)
    
    reference = query.first() 
    
    if print_query:
        print query
    return reference

def get_reference_from_id(reference_id, print_query=False):
    query = session.query(Reference).filter(Reference.id==reference_id)
    reference = query.first()
    if print_query:
        print query
    return reference

#Used to create go_overview and phenotype_overview tables
def get_reference_id(reference_name, print_query=False):
    '''
    get_reference_id('7635312', print_query=True)
    
    SELECT sprout.reference.reference_id AS sprout_reference_reference_id, sprout.reference.citation AS sprout_reference_citation, sprout.reference.fulltext_url AS sprout_reference_fulltext_url, sprout.reference.source AS sprout_reference_source, sprout.reference.status AS sprout_reference_status, sprout.reference.pdf_status AS sprout_reference_pdf_status, sprout.reference.dbxref_id AS sprout_reference_dbxref_id, sprout.reference.year AS sprout_reference_year, sprout.reference.pubmed_id AS sprout_reference_pubmed_id, sprout.reference.date_published AS sprout_reference_date_pu_1, sprout.reference.date_revised AS sprout_reference_date_revised, sprout.reference.issue AS sprout_reference_issue, sprout.reference.page AS sprout_reference_page, sprout.reference.volume AS sprout_reference_volume, sprout.reference.title AS sprout_reference_title, sprout.reference.journal_id AS sprout_reference_journal_id, sprout.reference.book_id AS sprout_reference_book_id, sprout.reference.doi AS sprout_reference_doi, sprout.reference.created_by AS sprout_reference_created_by, sprout.reference.date_created AS sprout_reference_date_created 
    FROM sprout.reference 
    WHERE sprout.reference.pubmed_id = :pubmed_id_1
    '''
    query = session.query(Reference).filter(Reference.format_name==reference_name)
        
    reference = query.first() 
    ref_id = None
    if reference is not None:
        ref_id = reference.id
    if print_query:
        print query
    return ref_id

#Used to create performance database.
def get_all_references(print_query=False):
    query = session.query(Reference)
    bioents = query.all()
    if print_query:
        print query
    return bioents

#Used to create performance database.
def get_all_urls(print_query=False):
    query = session.query(Url).filter(Url.class_type == 'REFERENCE')
    urls = query.all()
    if print_query:
        print query
    return urls

#Used for Author page.
def get_author(author_name, print_query=False):
    '''
    get_author('Brower_SM', print_query=True)

    SELECT sprout.author.author_id AS sprout_author_author_id, sprout.author.author_name AS sprout_author_author_name, sprout.author.created_by AS sprout_author_created_by, sprout.author.date_created AS sprout_author_date_created, author_reference_1.author_reference_id AS author_reference_1_autho_1, author_reference_1.author_order AS author_reference_1_autho_2, author_reference_1.author_type AS author_reference_1_author_type, author_reference_1.author_id AS author_reference_1_author_id, author_reference_1.reference_id AS author_reference_1_refer_3 
    FROM sprout.author LEFT OUTER JOIN sprout.author_reference author_reference_1 ON sprout.author.author_id = author_reference_1.author_id 
    WHERE sprout.author.author_name = :author_name_1
    '''
    query = session.query(Author).options(joinedload('author_references')).filter(Author.format_name==author_name)
    author = query.first()
    if print_query:
        print query
    return author

#Used for Author page.
def get_author_id(author_name, print_query=False):
    query = session.query(Author).filter(Author.format_name==author_name)
    author = query.first()
    author_id = None
    if author is not None:
        author_id = author.id
    if print_query:
        print query
    return author_id


#Used for Author page.
def get_assoc_reference(author_id=None, print_query=False):
    query = session.query(AuthorReference).options(joinedload('reference')).filter(AuthorReference.author_id==author_id)
    auth_refs = query.all()
    references = [auth_ref.reference for auth_ref in auth_refs]
    if print_query:
        print query
    return references

#Used to make bioent_names into links for reference abstracts.
def find_bioentities(text, print_query=False):
    """
    Find all bioentities (format_name/display_name) within a piece of text.
    """            
    
    name_to_feature = {}

    if text is not None and text != '':
        #words = text.upper().translate(string.maketrans("",""), string.punctuation).split()
        words = text.upper().split()
    
        upper_words = [x.upper() for x in words]
        bioents_by_format_name = set(session.query(Bioentity).filter(func.upper(Bioentity.format_name).in_(upper_words)).all())
        bioents_by_display_name = set(session.query(Bioentity).filter(func.upper(Bioentity.display_name).in_(upper_words)).all())
                  
        #Create table mapping name -> Feature        
        name_to_feature.update([(bioent.format_name, bioent) for bioent in bioents_by_format_name])
        name_to_feature.update([(bioent.display_name, bioent) for bioent in bioents_by_display_name])
              
    return name_to_feature

#Used for literature page
def get_references(bioent_ref_type, bioent_id=None, reference_id=None, print_query=False):
    query = session.query(BioentityReference).filter(BioentityReference.class_type==bioent_ref_type)
    if bioent_id is not None:
        query = query.filter(BioentityReference.bioentity_id==bioent_id)
    if reference_id is not None:
        query = query.filter(BioentityReference.reference_id==reference_id)
    bioent_refs = query.all()
    if print_query:
        print query
    return bioent_refs

#Used for literature overview
def get_all_references_for_bioent(bioent_id, print_query=False):
    query = session.query(BioentityReference).filter(BioentityReference.bioentity_id==bioent_id)
    bioent_refs = query.all()
    if print_query:
        print query
    return bioent_refs

#Used for reference_list_view
def get_reference_bibs(reference_ids=None, print_query=False):
    references = []
    if reference_ids is not None:
        query1 = session.query(Bibentry).filter(Bibentry.id.in_(reference_ids))
        references.extend(query1.all())
    else:
        query1 = session.query(Bibentry)
        references.extend(query1.all())
    if print_query:
        print query1
    return references
