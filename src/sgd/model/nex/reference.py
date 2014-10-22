from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from misc import Url, Alias, Relation, Source, Quality
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin

__author__ = 'kpaskov'


class AuthorReference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'author_reference'

    id = Column('author_reference_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    author_id = Column('author_id', Integer, ForeignKey(Author.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    order = Column('author_order', Integer)
    author_type = Column('author_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    author = relationship(Author, backref=backref('author_references', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('author_references', passive_deletes=True, order_by=order), uselist=False)
    author_name = association_proxy('author', 'display_name')

    __eq_values__ = ['id', 'order', 'author_type', 'created_by', 'date_created']
    __eq_fks__ = ['source', 'author', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.author_id, self.reference_id, self.order


class ReferenceReftype(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'reference_reftype'

    id = Column('reference_reftype_id', Integer, primary_key = True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    reftype_id = Column('reftype_id', Integer, ForeignKey(Reftype.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    reference = relationship(Reference, backref=backref('ref_reftypes', passive_deletes=True), uselist=False)
    reftype = relationship(Reftype, backref=backref('ref_reftypes', passive_deletes=True), uselist=False)

    __eq_values__ = ['id', 'created_by', 'date_created']
    __eq_fks__ = ['source', 'reference', 'reftype']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.reference_id, self.reftype_id

