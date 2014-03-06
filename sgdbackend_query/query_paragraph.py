'''
Created on Oct 26, 2013

@author: kpaskov
'''

from model_new_schema.paragraph import Paragraph, ParagraphReference
from sgdbackend_query import session
from sqlalchemy.orm import joinedload

#Used for regulation_overview
def get_paragraph(bioent_id, class_type, print_query=False):
    query = session.query(Paragraph).filter(Paragraph.bioentity_id == bioent_id).filter(Paragraph.class_type == class_type)
    paragraph = query.first()
    if print_query:
        print query
    return paragraph

def get_paragraph_references(reference_id, class_type):
    query = session.query(ParagraphReference).options(joinedload(ParagraphReference.paragraph)).filter(Paragraph.class_type == class_type).filter(ParagraphReference.reference_id == reference_id)
    return query.all()