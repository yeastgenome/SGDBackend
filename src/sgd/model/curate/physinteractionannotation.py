from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.taxonomy import Taxonomy
from src.sgd.model.curate.reference import Reference
from src.sgd.model.curate.locus import Locus

__author__ = 'sweng66'


class Physinteractionannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'physinteractionannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity1_id = Column('dbentity1_id', Integer, ForeignKey(Dbentity.id, ondelete='CASCADE'))
    dbentity2_id = Column('dbentity2_id', Integer, ForeignKey(Dbentity.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    bait_hit = Column('bait_hit', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    modification = Column('modification', String)
    annotation_type = Column('annotation_type', Integer)
    note = Column('note', String)
    
    #Relationships
    dbentity1 = relationship(Dbentity, uselist=False, backref='physinteraction_annotations', foreign_keys=[dbentity1_id])
    dbentity2 = relationship(Dbentity, uselist=False, foreign_keys=[dbentity2_id])
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    
    __eq_values__ = ['id', 'date_created', 'created_by', 'bait_hit', 'annotation_type', 'modification', 'note']
    __eq_fks__ = [('source', Source, False),
                  ('taxonomy', Taxonomy, False),
                  ('reference', Reference, False),
                  ('dbentity1', Dbentity, False),
                  ('dbentity2', Dbentity, False)]

    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity1_id', 'dbentity2_id', 'reference_id', 'bait_hit', 'modification', 'annotation_type']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    @classmethod
    def create_or_find(cls, obj_json, session):
        if obj_json is None:
            return None

        dbentity1, dbentity1_status = Dbentity.create_or_find(obj_json['dbentity1'], session)

        dbentity2, dbentity2_status = Dbentity.create_or_find(obj_json['dbentity2'], session)

        reference, reference_status = Reference.create_or_find(obj_json['reference'], session)

        if reference_status != 'Found':
            raise Exception('Reference not found: ' + str(obj_json['reference']))                

        if dbentity1_status != 'Found':
            raise Exception('Dbentity for dbentity1_id not found: ' + str(obj_json['dbentity1']))

        if dbentity2_status != 'Found':
            raise Exception('Dbentity for dbentity2_id not found: ' + str(obj_json['dbentity2']))

        query = session.query(cls)\
            .filter_by(dbentity1_id=dbentity.id)\
            .filter_by(dbentity2_id=dbentity.id)\
            .filter_by(reference_id=obj_json['reference_id'])\
            .filter_by(bait_hit=obj_json['bait_hit'])\
            .filter_by(modification=obj_json['modification'])\
            .filter_by(annotation_type=obj_json['annotation_type'])\

        current_obj = query.first()

        if current_obj is None:
            return cls(obj_json, session), 'Created'
        else:
            return current_obj, 'Found'

    def to_min_json(self, include_description=False):
        return self.to_json()
    def to_semi_json(self):
        return self.to_json()
