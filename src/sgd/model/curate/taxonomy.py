from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Taxonomy(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'taxonomy'

    id = Column('taxonomy_id', String, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    name = Column('name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    ncbi_taxon_id = Column('ncbi_taxon_id', Integer)
    common_name = Column('common_name', String)
    rank = Column('rank', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'description', 'bud_id', 'date_created', 'created_by',
                     'common_name', 'rank', 'ncbi_taxon_id']
    __eq_fks__ = [('source', Source, False),
                  ('aliases', 'taxonomy.TaxonomyAlias', True),
                  ('children', 'taxonomy.TaxonomyRelation', True)]
    __id_values__ = ['id', 'name', 'ncbi_taxon_id']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = ['rank']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)


class TaxonomyAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'taxonomy_alias'

    id = Column('alias_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', String, ForeignKey(Taxonomy.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    taxonomy = relationship(Taxonomy, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'alias_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.taxonomy is None else self.taxonomy.unique_key()), self.name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.taxonomy_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(taxonomy_id=newly_created_object.taxonomy_id)\
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


class TaxonomyRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'taxonomy_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    parent_id = Column('parent_id', String, ForeignKey(Taxonomy.id, ondelete='CASCADE'))
    child_id = Column('child_id', String, ForeignKey(Taxonomy.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Taxonomy, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Taxonomy, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('parent', Taxonomy, False),
                  ('child', Taxonomy, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, parent, child, relation_type):
        self.parent = parent
        self.child = child
        self.source = self.child.source
        self.relation_type = relation_type

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key(), self.relation_type)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Taxonomy.create_or_find(obj_json, session)
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