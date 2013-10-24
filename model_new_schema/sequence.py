'''
Created on Sep 23, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Bindingevidence(Evidence):
    __tablename__ = "bindingevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    link = Column('obj_url', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    total_score = Column('total_score', String)
    expert_confidence = Column('expert_confidence', String)
    motif_id = Column('motif_id', Integer)
       
    __mapper_args__ = {'polymorphic_identity': 'BINDING',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, strain, experiment, note, 
                 bioentity, total_score, expert_confidence, motif_id,
                 date_created, created_by):
        Evidence.__init__(self, 
                          bioentity.display_name + ' has binding site ' + str(motif_id),
                          bioentity.format_name + '|' + str(motif_id), 
                          'BINDING', source, reference, strain, experiment, note, date_created, created_by)
        self.bioentity_id = bioentity.id
        self.total_score = total_score
        self.expert_confidence = expert_confidence
        self.link = "/static/img/yetfasco/" + bioentity.format_name + "_" + str(motif_id) + ".0.png"
        self.motif_id = motif_id