from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Evidence
from src.sgd.model.nex.misc import Strain, Source, Experiment
from src.sgd.model.nex.reference import Reference


__author__ = 'kpaskov'

class ArchiveLiteratureevidence(Evidence):
    __tablename__ = "arch_literatureevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    topic = Column('topic', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    source = relationship(Source, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Bioentity, uselist=False, backref='arch_literature_evidences')

    __mapper_args__ = {'polymorphic_identity': "ARCH_LITERATURE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, bioentity, topic, date_created, created_by):
        Evidence.__init__(self, 'ARCH_LITERATURE', date_created, created_by)
        self.source_id = source.id
        self.reference_id = reference.id
        self.strain_id = None
        self.experiment_id = None
        self.note = None

        self.bioentity_id = None if bioentity is None else bioentity.id
        self.topic = topic

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.topic, self.reference_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['bioentity'] = self.bioentity.to_json()
        obj_json['reference'] = self.reference.to_semi_full_json()
        obj_json['topic'] = self.topic
        return obj_json