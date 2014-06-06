from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from src.sgd.model.nex.bioentity import Locus
from src.sgd.model.nex.evidence import Evidence
from src.sgd.model.nex.misc import Strain, Source, Experiment
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex import UpdateByJsonMixin
import json

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
    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))

    #Relationships
    source = relationship(Source, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('arch_literature_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref='arch_literature_evidences')

    __mapper_args__ = {'polymorphic_identity': "ARCH_LITERATURE", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'topic',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.json = json.dumps(self.to_json(aux_obj_json=obj_json))

    def unique_key(self):
        return self.class_type, self.locus_id, self.topic, self.reference_id