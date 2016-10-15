from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.ro import Ro

__author__ = 'sweng66'

class Eco(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'eco'

    id = Column('eco_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    ecoid = Column('ecoid', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by',
                     'ecoid']
    __eq_fks__ = [('source', Source, False),
                  ('aliases', 'eco.EcoAlias', True),
                  ('urls', 'eco.EcoUrl', True),
                  ('children', 'eco.EcoRelation', True)]
    __id_values__ = ['id', 'format_name', 'ecoid']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return obj_json['ecoid']


class EcoUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'eco_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    eco_id = Column('eco_id', Integer, ForeignKey(Eco.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    eco = relationship(Eco, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.eco is None else self.eco.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.eco_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(eco_id=newly_created_object.eco_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class EcoAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'eco_alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    eco_id = Column('eco_id', Integer, ForeignKey(Eco.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    eco = relationship(Eco, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'alias_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.eco is None else self.eco.unique_key()), self.display_name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.eco_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(eco_id=newly_created_object.eco_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(alias_type=newly_created_object.alias_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class EcoRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'eco_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    parent_id = Column('parent_id', Integer, ForeignKey(Eco.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Eco.id, ondelete='CASCADE'))
    ro_id = Column('ro_id', Integer, ForeignKey(Ro.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Eco, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Eco, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)
    ro = relationship(Ro, uselist=False)

    __eq_values__ = ['id', 'ro_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('ro', Ro, False),
                  ('parent', Eco, False),
                  ('child', Eco, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, parent, child, ro_id):
        self.parent = parent
        self.child = child
        self.source = self.child.source
        self.ro_id = ro_id

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Eco.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Child reference not found: ' + str(obj_json))

        ro_id = obj_json["ro_id"]

        current_obj = session.query(cls)\
            .filter_by(parent_id=parent_obj.id)\
            .filter_by(child_id=child.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, child, ro_id)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self):
        obj_json = self.child.to_min_json()
        obj_json['source'] = self.child.source.to_min_json()
        obj_json['ro'] = self.child.ro.to_min_json()
