from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.journal import Journal
from src.sgd.model.curate.book import Book
from src.sgd.model.curate.reftype import Reftype
from src.sgd.model.curate.author import Author
__author__ = 'kpaskov'

class Reference(Dbentity):
    __tablename__ = 'referencedbentity'

    id = Column('dbentity_id', String, ForeignKey(Dbentity.id), primary_key=True)
    method_obtained = Column('method_obtained', String)
    fulltext_status = Column('fulltext_status', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed_id = Column('pubmed_id', Integer)
    pubmed_central_id = Column('pubmed_central_id', String)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', Date)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', String, ForeignKey(Journal.id))
    book_id = Column('book_id', String, ForeignKey(Book.id))
    doi = Column('doi', String)

    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == Dbentity.id}
    __eq_values__ = ['id', 'name', 'link', 'description',
                     'bud_id', 'sgdid', 'dbentity_status', 'date_created', 'created_by',
                     'method_obtained', 'fulltext_status', 'citation', 'year', 'pubmed_id', 'pubmed_central_id', 'date_published', 'date_revised',
                     'issue', 'page', 'volume', 'title', 'doi']
    __eq_fks__ = [('source', Source, False),
                  ('journal', Journal, False),
                  ('book', Book, False),
                  ('aliases', 'reference.ReferenceAlias', True),
                  ('urls', 'reference.ReferenceUrl', True),
                  ('reftypes', 'reference.ReferenceReftype', False),
                  ('authors', 'reference.ReferenceAuthor', False),
                  ('children', 'reference.ReferenceRelation', False),
                  ('documents', 'reference.ReferenceDocument', True)]
    __id_values__ = ['id', 'sgdid', 'pubmed_id']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = ['fulltext_status', 'method_obtained', 'journal_id', 'book_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_name__(cls, obj_json):
        citation = obj_json['citation']
        return citation[:citation.find(")")+1]

    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['year'] = self.year
        return obj_json

    def __to_medium_json__(self):
        obj_json = ToJsonMixin.__to_medium_json__(self)
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['year'] = self.year
        obj_json['citation'] = self.citation
        obj_json['journal'] = None if self.journal is None else self.journal.med_abbr
        obj_json['urls'] = [x.to_json() for x in self.urls]
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['parents'] = [x.to_json(perspective='child') for x in self.parents]

        #interaction_locus_ids = set()
        #interaction_locus_ids.update([x.locus1_id for x in self.physinteraction_evidences])
        #interaction_locus_ids.update([x.locus2_id for x in self.physinteraction_evidences])
        #interaction_locus_ids.update([x.locus1_id for x in self.geninteraction_evidences])
        #interaction_locus_ids.update([x.locus2_id for x in self.geninteraction_evidences])
        #regulation_locus_ids = set()
        #regulation_locus_ids.update([x.locus1_id for x in self.regulation_evidences])
        #regulation_locus_ids.update([x.locus2_id for x in self.regulation_evidences])

        #obj_json['counts'] = {
        #    'interaction': len(interaction_locus_ids),
        #    'go': len(set([x.locus_id for x in self.go_evidences])),
        #    'phenotype': len(set([x.locus_id for x in self.phenotype_evidences])),
        #    'regulation': len(regulation_locus_ids)
        #}

        #id_to_dataset = {}
        #for expression_evidence in self.expression_evidences:
        #    if expression_evidence.datasetcolumn.dataset_id not in id_to_dataset:
        #        id_to_dataset[expression_evidence.datasetcolumn.dataset_id] = expression_evidence.datasetcolumn.dataset
        #obj_json['expression_datasets'] = [x.to_semi_json() for x in id_to_dataset.values()]
        return obj_json

class ReferenceUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_url'

    id = Column('url_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    reference_id = Column('reference_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'url_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), self.name, self.url_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.reference_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(reference_id=newly_created_object.reference_id)\
            .filter_by(name=newly_created_object.name)\
            .filter_by(url_type=newly_created_object.url_type).first()

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


class ReferenceAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_alias'

    id = Column('alias_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    reference_id = Column('reference_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'alias_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('reference', Reference, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), self.name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.reference_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(reference_id=newly_created_object.reference_id)\
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
            'source': self.source.to_json(size='small'),
            'alias_type': self.alias_type
        }


class ReferenceDocument(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_document'

    id = Column('document_id', Integer, primary_key=True)
    document_type = Column('document_type', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    reference_id = Column('reference_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('documents', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'document_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('reference', Reference, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), self.document_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.reference_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(reference_id=newly_created_object.reference_id)\
            .filter_by(document_type=newly_created_object.document_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'text': self.html,
            'source': self.source.to_json(size='small'),
            'document_type': self.document_type,
            'document_order': self.document_order,
            'references': []
        }


class ReferenceRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    parent_id = Column('parent_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    child_id = Column('child_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Reference, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Reference, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('parent', Reference, False),
                  ('child', Reference, False)]
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

        child, status = Reference.create_or_find(obj_json, session)
        if status == 'Created':
            raise Exception('Child reference not found: ' + str(obj_json))

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
            obj_json = self.child.to_json(size='medium')
            obj_json['documents'] = [x.to_json() for x in self.child.documents]
            obj_json['reftypes'] = [x.to_json(size='small', perspective='reference') for x in self.child.reftypes]
        elif perspective == 'child':
            obj_json = self.parent.to_json(size='medium')
            obj_json['documents'] = [x.to_json() for x in self.parent.documents]
            obj_json['reftypes'] = [x.to_json(size='small', perspective='reference') for x in self.parent.reftypes]

        if obj_json is not None:
            obj_json['relation_type'] = self.relation_type
        return obj_json


class ReferenceReftype(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_reftype'

    id = Column('reference_reftype_id', Integer, primary_key=True)
    reference_id = Column('reference_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    reftype_id = Column('reftype_id', String, ForeignKey(Reftype.id, ondelete='CASCADE'))
    source_id = Column('source_id', String, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('reftypes', cascade="all, delete-orphan", passive_deletes=True))
    reftype = relationship(Reftype, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('reference', Reference, False), ('reftype', Reftype, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, reference, reftype):
        self.reftype = reftype
        self.reference = reference
        self.source_id = self.reftype.source_id

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), (None if self.reftype is None else self.reftype.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        reftype, status = Reftype.create_or_find(obj_json, session)

        #if status == 'Created':
        #    raise Exception('Keyword not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(reference_id=parent_obj.id)\
            .filter_by(reftype_id=reftype.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, reftype)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small', perspective='reference'):
        if perspective == 'reference':
            obj_json = self.reftype.to_json(size=size)
        elif perspective == 'reftype':
            obj_json = self.reference.to_json(size=size)

        return obj_json


class ReferenceAuthor(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_author'

    id = Column('reference_author_id', Integer, primary_key=True)
    reference_id = Column('reference_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    author_id = Column('author_id', String, ForeignKey(Author.id, ondelete='CASCADE'))
    source_id = Column('source_id', String, ForeignKey(Source.id))
    author_order = Column('author_order', Integer)
    author_type = Column('author_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('authors', cascade="all, delete-orphan", passive_deletes=True))
    author = relationship(Author, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'date_created', 'created_by', 'author_order', 'author_type']
    __eq_fks__ = [('source', Source, False), ('reference', Reference, False), ('author', Author, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, reference, author, author_order, author_type):
        self.author_order = author_order
        self.author_type = author_type
        self.source = author.source
        self.reference = reference
        self.author = author

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), (None if self.author is None else self.author.unique_key(), self.author_order)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        author, status = Author.create_or_find(obj_json, session)

        #if status == 'Created':
        #    raise Exception('Author not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(reference_id=parent_obj.id)\
            .filter_by(author_id=author.id)\
            .filter_by(author_order=obj_json['author_order']).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, author, obj_json['author_order'], obj_json['author_type'])
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small', perspective='reference'):
        if perspective == 'reference':
            obj_json = self.author.to_json(size=size)
        elif perspective == 'author':
            obj_json = self.reference.to_json(size=size)

        if obj_json is not None:
            obj_json['author_order'] = self.author_order
            obj_json['author_type'] = self.author_type
        return obj_json
