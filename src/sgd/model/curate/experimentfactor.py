from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Experimentfactor(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'experimentfactor'

    id = Column('experimentfactor_id', String, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    name = Column('name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    efo_id = Column('efo_id', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'description', 'bud_id', 'date_created', 'created_by',
                     'efo_id']
    __eq_fks__ = [('source', Source, False),
                  ('aliases', 'experimentfactor.ExperimentfactorAlias', True),
                  ('urls', 'experimentfactor.ExperimentfactorUrl', True),
                  ('children', 'experimentfactor.ExperimentfactorRelation', True)]
    __id_values__ = ['id', 'efo_id', 'name']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)


class ExperimentfactorUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'experimentfactor_url'

    id = Column('url_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    experimentfactor_id = Column('experimentfactor_id', String, ForeignKey(Experimentfactor.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    experimentfactor = relationship(Experimentfactor, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'url_type',  'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.experimentfactor is None else self.experimentfactor.unique_key()), self.name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.experimentfactor_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(experimentfactor_id=newly_created_object.experimentfactor_id)\
            .filter_by(name=newly_created_object.name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'name': self.name,
            'link': self.link,
            'source': self.source.__to_small_json__(),
            'url_type': self.url_type
        }


class ExperimentfactorAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'experimentfactor_alias'

    id = Column('alias_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    experimentfactor_id = Column('experimentfactor_id', String, ForeignKey(Experimentfactor.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    experimentfactor = relationship(Experimentfactor, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'alias_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.experimentfactor is None else self.experimentfactor.unique_key()), self.name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.experimentfactor_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(experimentfactor_id=newly_created_object.experimentfactor_id)\
            .filter_by(name=newly_created_object.name)\
            .filter_by(alias_type=newly_created_object.alias_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'name': self.name,
            'link': self.link,
            'source': self.source.__to_small_json__(),
            'alias_type': self.alias_type
        }


class ExperimentfactorRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'experimentfactor_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    parent_id = Column('parent_id', String, ForeignKey(Experimentfactor.id, ondelete='CASCADE'))
    child_id = Column('child_id', String, ForeignKey(Experimentfactor.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Experimentfactor, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Experimentfactor, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('parent', Experimentfactor, False),
                  ('child', Experimentfactor, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, parent, child, relation_type):
        self.relation_type = relation_type
        self.source = child.source
        self.parent = parent
        self.child = child

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key(), self.relation_type)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Experimentfactor.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Child reference not found: ' + str(obj_json))

        relation_type = obj_json["relation_type"]

        current_obj = session.query(cls)\
            .filter_by(parent_id=parent_obj.id)\
            .filter_by(child_id=child.id)\
            .filter_by(relation_type=relation_type).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, child, relation_type)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small', perspective='parent'):
        if perspective == 'parent':
            obj_json = self.child.to_json(size='small')
        elif perspective == 'child':
            obj_json = self.parent.to_json(size='small')

        if obj_json is not None:
            obj_json['relation_type'] = self.relation_type
        return obj_json