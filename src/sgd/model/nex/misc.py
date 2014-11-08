from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin
from src.sgd.model.nex.basic import BasicObject, Source

__author__ = 'kpaskov'

       
class Url(EqualityByIDMixin, UpdateByJsonMixin, Base):
    __tablename__ = 'url'

    id = Column('id', Integer, primary_key=True)
    target_id = Column('target_id', Integer, ForeignKey(BasicObject.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    category = Column('category', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    references = association_proxy('url_references', 'reference')
    target = relationship(BasicObject, uselist=False, backref=backref('urls', passive_deletes=True))

    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'link', 'description']
    __fks__ = ['source', 'references']
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.target_id, self.display_name, self.category


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


class Alias(EqualityByIDMixin, UpdateByJsonMixin, Base):
    __tablename__ = 'alias'

    id = Column('id', Integer, primary_key=True)
    target_id = Column('target_id', Integer, ForeignKey(BasicObject.id))
    url_id = Column('url_id', Integer, ForeignKey(Url.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    category = Column('category', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    references = association_proxy('alias_references', 'reference')
    target = relationship(BasicObject, uselist=False, backref=backref('aliases', passive_deletes=True))
    url = relationship(Url, uselist=False, backref=backref('aliases', passive_deletes=True))
    link = association_proxy('url', 'link')

    __keys__ = ['id', 'display_name', 'format_name', 'description', 'date_created', 'created_by']
    __min_keys__ = ['id', 'display_name', 'format_name']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'description']
    __fks__ = ['source', 'references']
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.target_id, self.display_name, self.category


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


class Relation(EqualityByIDMixin, UpdateByJsonMixin, Base):
    __tablename__ = 'relation'

    id = Column('id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    category = Column('category', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    references = association_proxy('relation_references', 'reference')
    link = None

    __mapper_args__ = {'polymorphic_on': class_type}
    __keys__ = ['id', 'display_name', 'format_name', 'description', 'date_created', 'created_by']
    __min_keys__ = ['id', 'display_name', 'format_name']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'description']
    __fks__ = ['source', 'references']
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(self.parent_id) + ' - ' + str(self.child_id)
        self.display_name = str(self.parent_id) + ' - ' + str(self.child_id)

    def unique_key(self):
        return self.format_name, self.class_type, self.category


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


class Tag(EqualityByIDMixin, UpdateByJsonMixin, Base):
    __tablename__ = 'tag'

    id = Column('id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')

    __keys__ = ['id', 'display_name', 'format_name', 'description', 'date_created', 'created_by']
    __min_keys__ = ['id', 'display_name', 'format_name']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'description']
    __fks__ = ['source', 'references']
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)
        self.link = None if self.format_name is None else '/tag/' + self.format_name + '/overview'

    def unique_key(self):
        return self.format_name


class Tag_Basicobject(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'tag_basicobject'

    id = Column('id', Integer, primary_key=True)
    target_id = Column('target_id', Integer, ForeignKey(BasicObject.id))
    tag_id = Column('tag_id', Integer, ForeignKey(Tag.id))

    #Relationships
    target = relationship(BasicObject, uselist=False, backref=backref('tag_basicobjects', passive_deletes=True))
    tag = relationship(Tag, uselist=False, backref=backref('tag_basicobjects', passive_deletes=True))

    __keys__ = ['id', 'target_id', 'tag_id']
    __semi_keys__ = ['id', 'target_id', 'tag_id']
    __min_keys__ = ['id', 'target_id', 'tag_id']
    __fks__ = []
    __semi_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.target_id, self.tag_id


class Reference_Basicobject(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'reference_basicobject'

    id = Column('id', Integer, primary_key=True)
    target_id = Column('target_id', Integer, ForeignKey(BasicObject.id))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))
    category = Column('category', String)

    #Relationships
    target = relationship(BasicObject, uselist=False, backref=backref('reference_basicobjects', passive_deletes=True))
    reference = relationship('Reference', uselist=False, backref=backref('reference_basicobjects', passive_deletes=True))

    __keys__ = ['id', 'target_id', 'reference_id', 'category']
    __semi_keys__ = ['id', 'target_id', 'reference_id', 'category']
    __min_keys__ = ['id', 'target_id', 'reference_id', 'category']
    __fks__ = []
    __semi_fks__ = []
    __fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.target_id, self.reference_id, self.category


class Paragraph(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'paragraph'

    id = Column('id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey('bioentity.id'))
    category = Column('category', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    references = association_proxy('paragraph_references', 'reference')

    __keys__ = ['id', 'bioentity', 'category', 'text', 'html']
    __fks__ = ['references']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.bioentity_id, self.category


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