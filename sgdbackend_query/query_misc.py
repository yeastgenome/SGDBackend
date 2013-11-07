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

#Used for ontology graphs
def get_relations(cls, subclass_type, parent_ids=None, child_ids=None, print_query=False):
    query = session.query(cls)
    if subclass_type is not None:
        query = query.filter(cls.bioconrel_class_type==subclass_type)
    if (parent_ids is not None and len(parent_ids) == 0) or (child_ids is not None and len(child_ids) == 0):
        return []
    if parent_ids is not None:
        if len(parent_ids) == 1:
            query = query.filter(cls.parent_id==parent_ids[0])
        else:
            query = query.filter(cls.parent_id.in_(parent_ids))
    if child_ids is not None:
        if len(child_ids) == 1:
            query = query.filter(cls.child_id==child_ids[0])
        else:
            query = query.filter(cls.child_id.in_(child_ids))
      
    if print_query:
        print query
    return query.all()
