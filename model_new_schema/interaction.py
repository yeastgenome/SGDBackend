'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import BioentRelation
from model_new_schema.evidence import Evidence
from model_new_schema.link_maker import interaction_link, add_link
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Interaction(BioentRelation):
    __tablename__ = "interaction"

    id = Column('biorel_id', Integer, ForeignKey(BioentRelation.id), primary_key = True)
    physical_evidence_count = Column('physical_evidence_count', Integer)
    genetic_evidence_count = Column('genetic_evidence_count', Integer)
    evidence_count = Column('evidence_count', Integer)
    
    @hybrid_property
    def link(self):
        return interaction_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(str(self.display_name), self.link)
    @hybrid_property
    def description(self):
        return 'Interaction between ' + self.source_bioent.name_with_link + ' and ' + self.sink_bioent.name_with_link
        
    __mapper_args__ = {'polymorphic_identity': 'INTERACTION',
                       'inherit_condition': id == BioentRelation.id}
    
class Interevidence(Evidence):
    __tablename__ = "interevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    note = Column('note', String)
    annotation_type = Column('annotation_type', String)
    modification = Column('modification', String)
    direction = Column('direction', String)
    interaction_type = Column('interaction_type', String)
    biorel_id = Column('biorel_id', Integer, ForeignKey(Interaction.id))
    
    type = 'BIOREL_EVIDENCE'
    
    __mapper_args__ = {'polymorphic_identity': "INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    biorel = relationship(Interaction, backref='evidences')

    @hybrid_property
    def phenotype(self):
        if self.qualifier is not None:
            return self.qualifier + ' ' + self.observable
        else:
            return None
        
    def __init__(self, experiment_type, reference_id, strain_id, direction, annotation_type, modification, source, observable, qualifier, note, interaction_type, session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, experiment_type, reference_id, 'INTERACTION_EVIDENCE', strain_id, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.direction = direction
        self.annotation_type = annotation_type
        self.modification = modification
        self.source = source
        self.observable = observable
        self.qualifier = qualifier
        self.note = note
        self.interaction_type = interaction_type