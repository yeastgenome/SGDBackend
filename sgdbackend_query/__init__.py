from datetime import datetime, timedelta, time
from model_new_schema.auxiliary import Disambig, Interaction, Biofact
from model_new_schema.bioconcept import Bioconceptrelation
from model_new_schema.chemical import Chemicalrelation
from model_new_schema.condition import Condition, Temperaturecondition, \
    Bioentitycondition, Bioconceptcondition, Bioitemcondition, Generalcondition, \
    Chemicalcondition
from model_new_schema.evidence import Geninteractionevidence, \
    Physinteractionevidence, Regulationevidence, Evidence
from mpmath import ceil
from sgdbackend import DBSession
from sqlalchemy.orm import joinedload, subqueryload_all, subqueryload
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.sql.expression import func, or_

session = DBSession

#Useful methods
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    if identifier is None:
        return None
    
    query = session.query(Disambig).filter(func.lower(Disambig.disambig_key)==func.lower(str(identifier)))
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

def get_all(cls, print_query=False, join=None):
    query = session.query(cls)
    if join is not None:
        query = query.options(joinedload(join))
    objs = query.all()
    if print_query:
        print query
    return objs

two_bioent_evidence_cls = set([Geninteractionevidence, Physinteractionevidence, Regulationevidence])
def get_evidence(evidence_cls, bioent_id=None, biocon_id=None, chemical_id=None, reference_id=None, bioitem_id=None, with_children=False, print_query=False):
    ok_evidence_ids = None
    query = session.query(evidence_cls)
    
    if bioent_id is not None:
        if evidence_cls in two_bioent_evidence_cls:
            query = query.filter(or_(evidence_cls.bioentity1_id == bioent_id, evidence_cls.bioentity2_id == bioent_id))
        else:
            query = query.filter(evidence_cls.bioentity_id == bioent_id)
    if bioitem_id is not None:
        query = query.filter(evidence_cls.bioitem_id == bioitem_id)
    if chemical_id is not None:
        if ok_evidence_ids is None:
            ok_evidence_ids = set()
        if with_children:
            child_ids = list(get_all_chemical_children(chemical_id))
            num_chunks = ceil(1.0*len(child_ids)/500)
            for i in range(num_chunks):
                ok_evidence_ids.update([x.evidence_id for x in session.query(Chemicalcondition).filter(Chemicalcondition.chemical_id.in_(child_ids[i*500:(i+1)*500])).all()])
        else:
            ok_evidence_ids.update([x.evidence_id for x in session.query(Chemicalcondition).filter(Chemicalcondition.chemical_id == chemical_id).all()])
            
    if biocon_id is not None:
        if with_children:
            if ok_evidence_ids is None:
                ok_evidence_ids = set()
            child_ids = list(get_all_bioconcept_children(biocon_id))
            num_chunks = ceil(1.0*len(child_ids)/500)
            for i in range(num_chunks):
                ok_evidence_ids.update([x.id for x in session.query(evidence_cls).filter(evidence_cls.bioconcept_id.in_(child_ids[i*500:(i+1)*500])).all()])
        else:
            query = query.filter(evidence_cls.bioconcept_id == biocon_id)

    if reference_id is not None:
        query = query.filter(evidence_cls.reference_id == reference_id)

    if print_query:
        print query
        
    if ok_evidence_ids is None:
        if query.count() > 25000:
            return None
        else:
            return query.all()
    elif len(ok_evidence_ids) == 0:
        return []
    else:
        ok_evidence_ids = list(ok_evidence_ids)
        evidences = []
        num_chunks = ceil(1.0*len(ok_evidence_ids)/500)
        for i in range(num_chunks):
            evidences.extend([x for x in query.filter(evidence_cls.id.in_(ok_evidence_ids[i*500:(i+1)*500])).all()])

        if len(evidences) > 25000:
            return None
        return evidences

def get_all_bioconcept_children(parent_id):
    all_child_ids = set()
    new_parent_ids = [parent_id]
    while len(new_parent_ids) > 0:
        all_child_ids.update(new_parent_ids)
        if len(new_parent_ids) == 1:
            new_parent_ids = [x.child_id for x in session.query(Bioconceptrelation).filter(Bioconceptrelation.parent_id == new_parent_ids[0]).all()]
        else:
            num_chunks = ceil(1.0*len(new_parent_ids)/500)
            latest_list = []
            for i in range(num_chunks):
                latest_list.extend([x.child_id for x in session.query(Bioconceptrelation).filter(Bioconceptrelation.parent_id.in_(new_parent_ids[i*500:(i+1)*500])).all()])
            new_parent_ids = latest_list
    return all_child_ids

def get_bioconcept_parent_ids(bioconrel_type, bioconcept_ids):
    query = session.query(Bioconceptrelation).filter(Bioconceptrelation.bioconrel_class_type == bioconrel_type).filter(Bioconceptrelation.child_id.in_(bioconcept_ids))
    return [x.parent_id for x in query.all()]

def get_all_chemical_children(parent_id):
    all_child_ids = set()
    new_parent_ids = [parent_id]
    while len(new_parent_ids) > 0:
        all_child_ids.update(new_parent_ids)
        if len(new_parent_ids) == 1:
            new_parent_ids = [x.child_id for x in session.query(Chemicalrelation).filter(Chemicalrelation.parent_id == new_parent_ids[0]).all()]
        else:
            num_chunks = ceil(1.0*len(new_parent_ids)/500)
            latest_list = []
            for i in range(num_chunks):
                latest_list.extend([x.child_id for x in session.query(Chemicalrelation).filter(Chemicalrelation.parent_id.in_(new_parent_ids[i*500:(i+1)*500])).all()])
            new_parent_ids = latest_list
    return all_child_ids      

def get_conditions(evidence_ids, print_query=False):
    conditions = []
    num_chunks = ceil(1.0*len(evidence_ids)/500)
    for i in range(num_chunks):  
        this_chunk = evidence_ids[i*500:(i+1)*500]
        conditions.extend(session.query(Temperaturecondition).filter(Temperaturecondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Chemicalcondition).filter(Chemicalcondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Bioentitycondition).filter(Bioentitycondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Bioconceptcondition).filter(Bioconceptcondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Bioitemcondition).filter(Bioitemcondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(session.query(Generalcondition).filter(Generalcondition.evidence_id.in_(this_chunk)).all())
    return conditions

def get_evidence_snapshot(evidence_cls, attr_name):
    field = getattr(evidence_cls, attr_name)
    query = session.query(field, func.count(field)).group_by(field)
    return dict(query.all())

def get_evidence_over_time(subclass):
    earliest = session.query(func.min(Evidence.date_created)).filter(Evidence.class_type == subclass).first()[0]
    all_values = {}
    today = datetime.today().date()
    while earliest < today:
        earliest = earliest + timedelta(weeks=52)
        all_values[str(earliest)] = session.query(Evidence).filter(Evidence.class_type == subclass).filter(Evidence.date_created <= earliest).count()
    return all_values

def get_evidence_count(evidence_cls):
    return session.query(evidence_cls).count()

def get_interaction_snapshot(subclasses):
    query1 = session.query(Interaction.bioentity1_id, func.count(Interaction.bioentity1_id)).filter(Interaction.class_type.in_(subclasses)).group_by(Interaction.bioentity1_id)
    query2 = session.query(Interaction.bioentity2_id, func.count(Interaction.bioentity2_id)).filter(Interaction.class_type.in_(subclasses)).group_by(Interaction.bioentity2_id)
    bioentity1 = dict(query1.all())
    bioentity2 = dict(query2.all())
    for bioent_id, count in bioentity2.iteritems():
        if bioent_id in bioentity1:
            bioentity1[bioent_id] = bioentity1[bioent_id] + count
        else:
            bioentity1[bioent_id] = count
    return bioentity1

def get_snapshot_with_filter(cls, subclass, attr_name, filter_name):
    field = getattr(cls, attr_name)
    query = session.query(field, func.count(field)).filter(getattr(cls, filter_name) == subclass).group_by(field)
    return dict(query.all())