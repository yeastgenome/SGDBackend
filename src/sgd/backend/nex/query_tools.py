from math import ceil

from src.sgd.backend.nex import DBSession
from src.sgd.model.nex.bioentity import Bioentityurl
from src.sgd.model.nex.paragraph import Paragraph
from src.sgd.model.nex.auxiliary import Interaction
from sqlalchemy.orm import joinedload


__author__ = 'kpaskov'

def get_all_bioconcept_children(parent_id):
    from src.sgd.model.nex.bioconcept import Bioconceptrelation
    all_child_ids = set()
    new_parent_ids = [parent_id]
    while len(new_parent_ids) > 0:
        all_child_ids.update(new_parent_ids)
        if len(new_parent_ids) == 1:
            new_parent_ids = [x.child_id for x in DBSession.query(Bioconceptrelation).filter(relation_type = 'part of').filter(Bioconceptrelation.parent_id == new_parent_ids[0]).all()]
        else:
            num_chunks = int(ceil(1.0*len(new_parent_ids)/500))
            latest_list = []
            for i in range(num_chunks):
                latest_list.extend([x.child_id for x in DBSession.query(Bioconceptrelation).filter(relation_type = 'part of').filter(Bioconceptrelation.parent_id.in_(new_parent_ids[i*500:(i+1)*500])).all()])
            new_parent_ids = latest_list
    return all_child_ids

def get_interactions(interaction_type, bioent_id):
    query = DBSession.query(Interaction).filter(Interaction.bioentity_id == bioent_id).filter(Interaction.interaction_type==interaction_type)
    return query.all()

def get_interactions_among(interaction_type, bioent_ids, interactor_ids):
    interactions = []
    if len(bioent_ids) > 0 and len(interactor_ids) > 0:
        query = DBSession.query(Interaction).filter(Interaction.interaction_type==interaction_type).filter(
                                              Interaction.bioentity_id.in_(bioent_ids)).filter(
                                              Interaction.interactor_id.in_(interactor_ids))
        interactions = query.all()
    return interactions

def get_paragraph(bioent_id, class_type):
    query = DBSession.query(Paragraph).filter(Paragraph.bioentity_id == bioent_id).filter(Paragraph.class_type == class_type)
    paragraph = query.first()
    return paragraph

def get_urls(category, bioent_id=None):
    query = DBSession.query(Bioentityurl)
    if bioent_id is not None:
        query = query.filter(Bioentityurl.bioentity_id==bioent_id).filter(Bioentityurl.category==category)
    return query.all()

#Used for ontology graphs
def get_relations(cls, subclass_type, parent_ids=None, child_ids=None):
    query = DBSession.query(cls).options(joinedload('child'), joinedload('parent'))
    if subclass_type is not None:
        query = query.filter(cls.relation_type==subclass_type)
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
    return query.all()