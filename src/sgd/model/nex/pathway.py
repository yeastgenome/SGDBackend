from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, Float, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import ToJsonMixin, UpdateWithJsonMixin, Base
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.reference import Reference

__author__ = 'sweng66'

class Pathway(Dbentity):
    __tablename__ = 'pathwaydbentity'

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)
    biocyc_id = Column('biocyc_id', String)
    
    #Relationships

    __mapper_args__ = {'polymorphic_identity': 'PATHWAY', 'inherit_condition': id == Dbentity.id}

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'date_created', 
                     'created_by', 'sgdid', 'dbentity_status', 'biocyc_id']
    __eq_fks__ = [('source', Source, False),
                  ('urls', 'pathway.PathwayUrl', True),
                  ('aliases', 'pathway.PathwayAlias', True),
                  ('summaries', 'pathway.PathwaySummary', True)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['biocyc_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json


class PathwayUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'pathway_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    pathway_id = Column('pathway_id', Integer, ForeignKey(Pathway.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    pathway = relationship(Pathway, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('pathway', Pathway, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.pathway is None else self.pathway.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.pathway_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(pathway_id=newly_created_object.pathway_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class PathwayAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'pathway_alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    pathway_id = Column('pathway_id', Integer, ForeignKey(Pathway.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships                                                                                                                                                                                                                      
    pathway = relationship(Pathway, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'alias_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('pathway', Pathway, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.pathway is None else self.pathway.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.pathway_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(pathway_id=newly_created_object.pathway_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

class PathwaySummary(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'pathway_summary'

    id = Column('summary_id', Integer, primary_key=True)
    summary_type = Column('summary_type', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    pathway_id = Column('pathway_id', Integer, ForeignKey(Pathway.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    pathway = relationship(Pathway, uselist=False, backref=backref('summaries', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'summary_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('pathway', Pathway, False),
                  ('references', 'pathway.PathwaySummaryReference', False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.pathway is None else self.pathway.unique_key()), self.summary_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.pathway_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(pathway_id=newly_created_object.pathway_id)\
            .filter_by(summary_type=newly_created_object.summary_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class PathwaySummaryReference(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'pathway_summary_reference'

    id = Column('summary_reference_id', Integer, primary_key=True)
    summary_id = Column('summary_id', Integer, ForeignKey(PathwaySummary.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    reference_order = Column('reference_order', Integer)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    summary = relationship(PathwaySummary, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    reference = relationship(Reference, uselist=False, backref=backref('pathway_summaries', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'reference_order', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('summary', PathwaySummary, False),
                  ('reference', Reference, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, summary, reference_id, reference_order):
        self.reference_order = reference_order
        self.summary = summary
        self.reference_id = reference_id
        self.source = self.summary.source

    def unique_key(self):
        return (None if self.summary is None else self.summary.unique_key()), (None if self.reference is None else self.reference.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        # reference, status = Reference.create_or_find(obj_json, session)
        # if status == 'Created':
        #    raise Exception('Reference not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(summary_id=parent_obj.id)\
            .filter_by(reference_id=obj_json['reference_id'])

        if current_obj is None:
            newly_created_object = cls(parent_obj, obj_json['reference_id'], obj_json['reference_order'])
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'
