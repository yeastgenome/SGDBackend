from model_new_schema.auxiliary import Locustabs, Disambig
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity, Locus, Bioentityurl
from model_new_schema.chemical import Chemical
from model_new_schema.condition import Condition, Temperaturecondition, \
    Bioentitycondition, Bioconceptcondition, Bioitemcondition
from model_new_schema.evidence import Geninteractionevidence, \
    Physinteractionevidence, Regulationevidence
from model_new_schema.misc import Url
from model_new_schema.paragraph import Paragraph
from model_new_schema.reference import Reference, Author, AuthorReference
from mpmath import ceil
from sgdbackend import DBSession
from sqlalchemy.orm import joinedload, subqueryload_all, subqueryload
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.sql.expression import func, or_
import datetime
import math
import model_new_schema

session = DBSession

#Useful methods
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    if identifier is None:
        return None
    
    query = session.query(Disambig).filter(Disambig.disambig_key==identifier.upper())
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    if len(disambigs) > 0:
        return [(disambig.identifier, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
    return None

def get_obj_id(identifier, class_type=None, subclass_type=None):
    objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
    obj_id = None if objs_ids is None or len(objs_ids) != 1 else objs_ids[0][0]
    return obj_id

def get_multi_obj_ids(identifiers, class_type=None, subclass_type=None, print_query=False):
    if identifiers is None:
        return None
    
    cleaned_up_ids = filter(None, [x.upper() for x in identifiers])
    query = session.query(Disambig).filter(Disambig.disambig_key.in_(cleaned_up_ids))
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    disambig_dict = {}
    for disambig in disambigs:
        obj_id = disambig.identifier
        key = disambig.disambig_key
        
        if key in disambig_dict:
            disambig_dict[key].append(obj_id)
        else:
            disambig_dict[key] = [obj_id]
        
    return disambig_dict

def get_all(cls, print_query=False):
    query = session.query(cls)
    objs = query.all()
    if print_query:
        print query
    return objs

def get_relations(obj_ids, relation_cls, print_query=False):
    obj_id_set = set(obj_ids)
    related_objs = set()
    
    query1 = session.query(relation_cls).filter(relation_cls.parent_id.in_(obj_id_set))
    children = query1.all()
    obj_ids.update([x for x in children if x.child_id in obj_id_set])
    
    query2 = session.query(relation_cls).filter(relation_cls.child_id.in_(obj_id_set))
    parents = query2.all()
    related_objs.update([x for x in parents if x.parent_id in obj_id_set])
    
    if print_query:
        print query1
        print query2
    return related_objs

two_bioent_evidence_cls = set([Geninteractionevidence, Physinteractionevidence, Regulationevidence])
def get_evidence(evidence_cls, bioent_id=None, biocon_id=None, print_query=False):
    query = session.query(evidence_cls)
    if bioent_id is not None:
        if evidence_cls in two_bioent_evidence_cls:
            query = query.filter(or_(evidence_cls.bioentity1_id == bioent_id, evidence_cls.bioentity2_id == bioent_id))
        else:
            query = query.filter(evidence_cls.bioentity_id == bioent_id)
    if biocon_id is not None:
        query = query.filter(evidence_cls.bioconcept_id == biocon_id)
        
    evidence = query.all()
    
    if print_query:
        print query
    return evidence

def get_conditions(evidence_ids, print_query=False):
    conditions = []
    num_chunks = ceil(1.0*len(evidence_ids)/500)
    for i in range(num_chunks):  
        this_chunk = evidence_ids[i*500:(i+1)*500]
        conditions.extend(session.query(Temperaturecondition).filter(Condition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Bioentitycondition).filter(Condition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Bioconceptcondition).filter(Condition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Bioitemcondition).filter(Condition.evidence_id.in_(this_chunk)).all())
    
    return conditions
    
