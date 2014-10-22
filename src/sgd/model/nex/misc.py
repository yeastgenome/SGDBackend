from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, BasicObject, create_format_name, UpdateByJsonMixin

__author__ = 'kpaskov'

       
class Url(BasicObject):
    __tablename__ = 'url'

    id = Column('id', Integer, primary_key=True)
    class_type = Column('class', String)
    category = Column('category', String)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    references = association_proxy('url_references', 'reference')

    __mapper_args__ = {'polymorphic_on': class_type}
    __fks__ = ['source', 'references']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.category, self.display_name, self.format_name


class UrlsReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'url_reference'

    id = Column('id', Integer, primary_key=True)
    alias_id = Column('url_id', Integer, ForeignKey(Url.id))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))

    #Relationships
    url = relationship(Url, uselist=False, backref=backref('url_references', passive_deletes=True))
    reference = relationship('Reference', uselist=False, backref=backref('url_references', passive_deletes=True))

    __keys__ = ['id', 'url_id', 'reference_id']
    __semi_keys__ = ['id', 'url_id', 'reference_id']
    __min_keys__ = ['id', 'url_id', 'reference_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.url_id, self.reference_id


class PrimaryUrl(Url):
    __tablename__ = 'primaryurl'

    id = Column('id', Integer, ForeignKey(Url.id), primary_key=True)
    primary_id = Column('primary_id', Integer, ForeignKey('primary.id'))

    #Relationships
    primary = relationship('Primary', uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'PRIMARY', 'inherit_condition': id == Url.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'category', 'date_created', 'created_by', 'class_type', 'primary_id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.primary_id is None else str(self.primary_id)


class SecondaryUrl(Url):
    __tablename__ = 'secondaryurl'

    id = Column('id', Integer, ForeignKey(Url.id), primary_key=True)
    secondary_id = Column('secondary_id', Integer, ForeignKey('secondary.id'))

    #Relationships
    secondary = relationship('Secondary', uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'SECONDARY', 'inherit_condition': id == Url.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'category', 'date_created', 'created_by', 'class_type', 'secondary_id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.secondary_id is None else str(self.secondary_id)


class Alias(BasicObject):
    __tablename__ = 'alias'

    id = Column('id', Integer, primary_key=True)
    class_type = Column('class', String)
    category = Column('category', String)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    references = association_proxy('alias_references', 'reference')

    __mapper_args__ = {'polymorphic_on': class_type}
    __fks__ = ['source', 'references']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.category, self.display_name, self.format_name


class AliasReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'alias_reference'

    id = Column('id', Integer, primary_key=True)
    alias_id = Column('alias_id', Integer, ForeignKey(Alias.id))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))

    #Relationships
    alias = relationship(Alias, uselist=False, backref=backref('alias_references', passive_deletes=True))
    reference = relationship('Reference', uselist=False, backref=backref('alias_references', passive_deletes=True))

    __keys__ = ['id', 'alias_id', 'reference_id']
    __semi_keys__ = ['id', 'alias_id', 'reference_id']
    __min_keys__ = ['id', 'alias_id', 'reference_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.alias_id, self.reference_id


class PrimaryAlias(Alias):
    __tablename__ = 'primaryalias'

    id = Column('id', Integer, ForeignKey(Url.id), primary_key=True)
    primary_id = Column('primary_id', Integer, ForeignKey('primary.id'))

    #Relationships
    primary = relationship('Primary', uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'PRIMARY', 'inherit_condition': id == Alias.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'category', 'date_created', 'created_by', 'class_type', 'primary_id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.primary_id is None else str(self.primary_id)


class SecondaryAlias(Alias):
    __tablename__ = 'secondaryalias'

    id = Column('id', Integer, ForeignKey(Url.id), primary_key=True)
    secondary_id = Column('secondary_id', Integer, ForeignKey('secondary.id'))

    #Relationships
    secondary = relationship('Secondary', uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'SECONDARY', 'inherit_condition': id == Alias.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'category', 'date_created', 'created_by', 'class_type', 'secondary_id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.secondary_id is None else str(self.secondary_id)


class Relation(BasicObject):
    __tablename__ = 'relation'

    id = Column('id', Integer, primary_key=True)
    class_type = Column('class', String)
    category = Column('category', String)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    references = association_proxy('relation_references', 'reference')

    __mapper_args__ = {'polymorphic_on': class_type}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'category', 'date_created', 'created_by', 'class_type', 'parent_id', 'child_id']
    __fks__ = ['source', 'references']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(self.parent_id) + ' - ' + str(self.child_id)
        self.display_name = str(self.parent_id) + ' - ' + str(self.child_id)

    def unique_key(self):
        return self.class_type, self.category, self.format_name


class RelationReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'relation_reference'

    id = Column('id', Integer, primary_key=True)
    relation_id = Column('relation_id', Integer, ForeignKey(Relation.id))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))

    #Relationships
    relation = relationship(Relation, uselist=False, backref=backref('relation_references', passive_deletes=True))
    reference = relationship('Reference', uselist=False, backref=backref('relation_references', passive_deletes=True))

    __keys__ = ['id', 'relation_id', 'reference_id']
    __semi_keys__ = ['id', 'relation_id', 'reference_id']
    __min_keys__ = ['id', 'relation_id', 'reference_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.relation_id, self.reference_id


class PrimaryRelation(Relation):
    __tablename__ = 'primaryrelation'

    id = Column('id', Integer, ForeignKey(Url.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey('primary.id'))
    child_id = Column('child_id', Integer, ForeignKey('primary.id'))

    #Relationships
    parent = relationship('Primary', backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship('Primary', backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'PRIMARY', 'inherit_condition': id == Relation.id}


class SecondaryRelation(Relation):
    __tablename__ = 'secondaryrelation'

    id = Column('id', Integer, ForeignKey(Url.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey('secondary.id'))
    child_id = Column('child_id', Integer, ForeignKey('secondary.id'))

    #Relationships
    parent = relationship('Secondary', backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship('Secondary', backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'SECONDARY', 'inherit_condition': id == Relation.id}


class Tag(BasicObject):
    __tablename__ = 'tag'

    id = Column('id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')

    __fks__ = ['source', 'primary_tags', 'secondary_tags']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)
        self.link = None if self.format_name is None else '/tag/' + self.format_name + '/overview'

    def unique_key(self):
        return self.format_name


class PrimaryTag(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'primary_tag'

    id = Column('id', Integer, primary_key=True)
    secondary_id = Column('primary_id', Integer, ForeignKey('primary.id'))
    tag_id = Column('tag_id', Integer, ForeignKey(Tag.id))

    #Relationships
    secondary = relationship('Primary', uselist=False, backref=backref('primary_tags', passive_deletes=True))
    tag = relationship(Tag, uselist=False, backref=backref('primary_tags', passive_deletes=True))

    __keys__ = ['id', 'primary_id', 'tag_id']
    __semi_keys__ = ['id', 'primary_id', 'tag_id']
    __min_keys__ = ['id', 'primary_id', 'tag_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.primary_id, self.tag_id


class SecondaryTag(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'secondary_tag'

    id = Column('id', Integer, primary_key=True)
    secondary_id = Column('secondary_id', Integer, ForeignKey('secondary.id'))
    tag_id = Column('tag_id', Integer, ForeignKey(Tag.id))

    #Relationships
    secondary = relationship('Secondary', uselist=False, backref=backref('secondary_tags', passive_deletes=True))
    tag = relationship(Tag, uselist=False, backref=backref('secondary_tags', passive_deletes=True))

    __keys__ = ['id']
    __fks__ = ['secondary', 'tag']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.secondary_id, self.tag_id


class Quality(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'quality'

    id = Column('id', Integer, primary_key=True)
    primary_id = Column('primary_id', Integer, ForeignKey('primary.id'))
    key = Column('key', String)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    references = association_proxy('quality_references', 'reference')

    __keys__ = ['id', 'primary_id', 'key']
    __fks__ = ['references']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.primary_id, self.key


class QualityReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'quality_reference'

    id = Column('id', Integer, primary_key=True)
    quality_id = Column('quality_id', Integer, ForeignKey(Quality.id))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))

    #Relationships
    relation = relationship(Quality, uselist=False, backref=backref('quality_references', passive_deletes=True))
    reference = relationship('Reference', uselist=False, backref=backref('quality_references', passive_deletes=True))

    __keys__ = ['id', 'quality_id', 'reference_id']
    __semi_keys__ = ['id', 'quality_id', 'reference_id']
    __min_keys__ = ['id', 'quality_id', 'reference_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.quality_id, self.reference_id


class Paragraph(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph'

    id = Column('id', Integer, primary_key=True)
    primary_id = Column('primary_id', Integer, ForeignKey('primary.id'))
    category = Column('category', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    references = association_proxy('paragraph_references', 'reference')

    __keys__ = ['id', 'primary_id', 'category', 'text', 'html']
    __fks__ = ['references']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.format_name, self.class_type, self.category


class ParagraphReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph_reference'

    id = Column('id', Integer, primary_key=True)
    paragraph_id = Column('paragraph_id', Integer, ForeignKey(Paragraph.id))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))

    #Relationships
    paragraph = relationship(Paragraph, uselist=False, backref=backref('paragraph_references', passive_deletes=True))
    reference = relationship('Reference', uselist=False, backref=backref('paragraph_references', passive_deletes=True))

    __keys__ = ['id', 'paragraph_id', 'reference_id']
    __semi_keys__ = ['id', 'paragraph_id', 'reference_id']
    __min_keys__ = ['id', 'paragraph_id', 'reference_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.paragraph_id, self.reference_id