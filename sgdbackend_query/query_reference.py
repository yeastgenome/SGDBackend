'''
Created on Jul 9, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.reference import Bibentry, Abstract, AuthorReference, Author
from sgdbackend_query import session
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

#Used to make bioent_names into links for reference abstracts.
from sgdbackend_utils import id_to_reference
from sgdbackend_utils.obj_to_json import author_to_json


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

#Used for reference_list_view
def get_reference_bibs(reference_ids=None, min_id=None, max_id=None, print_query=False):
    references = []
    query1 = session.query(Bibentry)
    if reference_ids is not None:
        query1 = query1.filter(Bibentry.id.in_(reference_ids))
    if min_id is not None:
        query1 = query1.filter(Bibentry.id >= min_id)
    if max_id is not None:
        query1 = query1.filter(Bibentry.id < max_id)
    references.extend(query1.all())
    if print_query:
        print query1
    return references

#Used for reference_overview
def get_abstract(reference_id, print_query=False):
    query = session.query(Abstract).filter(Abstract.id == reference_id)
    abstracts = query.all()
    if len(abstracts) == 1:
        return abstracts[0].text
    return None

def get_bibentry(reference_id, print_query=False):
    query = session.query(Bibentry).filter(Bibentry.id == reference_id)
    bibentries = query.all()
    if len(bibentries) == 1:
        return bibentries[0].text
    return None

def get_authors(reference_id, print_query=False):
    query = session.query(AuthorReference).options(joinedload("author")).filter(AuthorReference.reference_id == reference_id)
    author_refs = query.all()
    author_refs.sort(key=lambda x: x.order)
    return [author_to_json(author_ref.author) for author_ref in author_refs]

def get_author(author_identifier):
    try:
        author_id = int(author_identifier)
        query = session.query(Author).filter(Author.id == author_id)
    except:
        query = session.query(Author).filter(Author.format_name == author_identifier)
    author = query.first()
    return None if author is None else author_to_json(author)

def get_references_for_author(author_id, print_query=False):
    query = session.query(AuthorReference).filter(AuthorReference.author_id == author_id)
    author_refs = query.all()
    return [id_to_reference[author_ref.reference_id] for author_ref in author_refs]