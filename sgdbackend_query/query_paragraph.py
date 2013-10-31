'''
Created on Oct 26, 2013

@author: kpaskov
'''

from model_new_schema.paragraph import Paragraph
from sgdbackend_query import session

#Used for regulation_overview
def get_paragraph(bioent_id, class_type, print_query=False):
    query = session.query(Paragraph).filter(Paragraph.bioentity_id == bioent_id).filter(Paragraph.class_type == class_type)
    paragraph = query.first()
    if print_query:
        print query
    return paragraph