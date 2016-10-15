from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.so import So
from src.sgd.model.nex.ro import Ro
from src.sgd.model.nex.locus import Locus

__author__ = 'sweng66'

class Locussummary(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locussummary'

    id = Column('summary_id', Integer, primary_key=True)
    summary_type = Column('summary_type', String)
    summary_order = Column('summary_order', Integer)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    # locus = relationship(Locus, uselist=False, backref=backref('summaries', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'summary_type', 'summary_order',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('references', 'locussummary.LocussummaryReference', True)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.locus_id = obj_json['locus_id']
        if 'bud_id' in obj_json:
            self.bud_id = obj_json['bud_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.locus_id, self.summary_type, self.summary_order

    @classmethod
    def create_or_find(cls, obj_json, session):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
    
        current_obj = session.query(cls)\
            .filter_by(locus_id=newly_created_object.locus_id)\
            .filter_by(summary_type=newly_created_object.summary_type)\
            .filter_by(summary_order=newly_created_object.summary_order).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_semi_json(self):
        return self.to_min_json()

    def to_min_json(self):
        obj_json = ToJsonMixin.to_min_json(self)
        obj_json['text'] = self.html
        obj_json['summary_type'] = self.summary_type
        obj_json['summary_order'] = self.summary_order
        return obj_json


class LocussummaryReference(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locussummary_reference'

    id = Column('summary_reference_id', Integer, primary_key=True)
    summary_id = Column('summary_id', Integer, ForeignKey(Locussummary.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    reference_order = Column('reference_order', Integer)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    summary = relationship(Locussummary, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    reference = relationship(Reference, uselist=False, backref=backref('locussummaries', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'reference_id', 'reference_order', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, summary, reference, reference_order):
        self.reference_order = reference_order
        self.summary = summary
        self.reference_id = reference.id
        self.source = self.summary.source

    def unique_key(self):
        return self.summary, self.reference_id, self.reference_order

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        reference, status = Reference.create_or_find(obj_json, session)
        if status == 'Created':
            raise Exception('Reference not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(summary_id=parent_obj.id)\
            .filter_by(reference_id=reference.id).first()
    
        if current_obj is None:
            newly_created_object = cls(parent_obj, reference, obj_json['reference_order'])
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'





