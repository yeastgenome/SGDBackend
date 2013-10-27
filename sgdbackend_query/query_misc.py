'''
Created on Oct 26, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentityurl
from sgdbackend_query import session

#Used for Interaction resources
def get_urls(category, bioent_id=None, print_query=False):
    query = session.query(Bioentityurl)
    if bioent_id is not None:
        query = query.filter(Bioentityurl.bioentity_id==bioent_id).filter(Bioentityurl.category==category)
    urls = query.all()
    if print_query:
        print query
    return urls

