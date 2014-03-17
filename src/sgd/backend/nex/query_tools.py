from math import ceil

from sqlalchemy.sql.expression import or_

from src.sgd.backend.nex import DBSession
from src.sgd.model.nex.auxiliary import BioentityReference, Biofact, Interaction
from src.sgd.model.nex.bioentity import Bioentityurl
from src.sgd.model.nex.paragraph import Paragraph


__author__ = 'kpaskov'

def get_all_bioconcept_children(parent_id):
    from src.sgd.model.nex.bioconcept import Bioconceptrelation
    all_child_ids = set()
    new_parent_ids = [parent_id]
    while len(new_parent_ids) > 0:
        all_child_ids.update(new_parent_ids)
        if len(new_parent_ids) == 1:
            new_parent_ids = [x.child_id for x in DBSession.query(Bioconceptrelation).filter(Bioconceptrelation.parent_id == new_parent_ids[0]).all()]
        else:
            num_chunks = int(ceil(1.0*len(new_parent_ids)/500))
            latest_list = []
            for i in range(num_chunks):
                latest_list.extend([x.child_id for x in DBSession.query(Bioconceptrelation).filter(Bioconceptrelation.parent_id.in_(new_parent_ids[i*500:(i+1)*500])).all()])
            new_parent_ids = latest_list
    return all_child_ids

def get_conditions(evidence_ids):
    from src.sgd.model.nex.condition import Temperaturecondition, Chemicalcondition, Bioentitycondition, Bioconceptcondition, Bioitemcondition, Generalcondition
    conditions = []
    num_chunks = int(ceil(1.0*len(evidence_ids)/500))
    for i in range(num_chunks):
        this_chunk = evidence_ids[i*500:(i+1)*500]
        conditions.extend(DBSession.query(Temperaturecondition).filter(Temperaturecondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(DBSession.query(Chemicalcondition).filter(Chemicalcondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(DBSession.query(Bioentitycondition).filter(Bioentitycondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(DBSession.query(Bioconceptcondition).filter(Bioconceptcondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(DBSession.query(Bioitemcondition).filter(Bioitemcondition.evidence_id.in_(this_chunk)).all())
        conditions.extend(DBSession.query(Generalcondition).filter(Generalcondition.evidence_id.in_(this_chunk)).all())
    return conditions

def get_interactions(interaction_type, bioent_id):
    query = DBSession.query(Interaction).filter(
                                or_(Interaction.bioentity1_id == bioent_id,
                                    Interaction.bioentity2_id == bioent_id)).filter(
                                Interaction.class_type==interaction_type)
    return query.all()

def get_interactions_among(interaction_type, bioent_ids, min_evidence_count):
    interactions = []
    if len(bioent_ids) > 0:
        query = DBSession.query(Interaction).filter(
                                              Interaction.class_type==interaction_type).filter(
                                              Interaction.bioentity1_id.in_(bioent_ids)).filter(
                                              Interaction.bioentity2_id.in_(bioent_ids)).filter(
                                              Interaction.evidence_count >= min_evidence_count)
        interactions = query.all()
    return interactions

def get_bioentity_references(class_type=None, bioent_id=None, reference_id=None, bioent_ids=None, reference_ids=None):
    query = DBSession.query(BioentityReference)
    if class_type is not None:
        query = query.filter(BioentityReference.class_type == class_type)
    if bioent_id is not None:
        query = query.filter(BioentityReference.bioentity_id == bioent_id)
    if reference_id is not None:
        query = query.filter(BioentityReference.reference_id == reference_id)
    if bioent_ids is not None:
        query = query.filter(BioentityReference.bioentity_id.in_(bioent_ids))
    if reference_ids is not None:
        query = query.filter(BioentityReference.reference_id.in_(reference_ids))
    return query.all()

def get_biofacts(biocon_type, biocon_id=None, bioent_id=None, bioent_ids=None, biocon_ids=None, bioent_type=None):
    query = DBSession.query(Biofact).filter(Biofact.bioconcept_class_type==biocon_type)
    if bioent_type is not None:
        query = query.filter(Biofact.bioentity_class_type == bioent_type)
    if bioent_id is not None:
        query = query.filter(Biofact.bioentity_id==bioent_id)
    if biocon_id is not None:
        query = query.filter(Biofact.bioconcept_id==biocon_id)
    if bioent_ids is not None:
        query = query.filter(Biofact.bioentity_id.in_(bioent_ids))
    if biocon_ids is not None:
        query = query.filter(Biofact.bioconcept_id.in_(biocon_ids))
    return query.all()

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
    query = DBSession.query(cls)
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
    return query.all()