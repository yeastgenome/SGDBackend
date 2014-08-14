from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from misc import Url, Alias, Relation, Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin

__author__ = 'kpaskov'

class Book(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'book'

    id = Column('book_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'title', 'volume_title', 'isbn', 'total_pages',
                     'publisher', 'publisher_location',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = self.title
        self.format_name = create_format_name(self.title + '' if self.volume_title is None else ('_' + self.volume_title))

    def unique_key(self):
        return self.title, self.volume_title

class Journal(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'journal'

    id = Column('journal_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    title = Column('title', String)
    med_abbr = Column('med_abbr', String)
    issn_print = Column('issn_print', String)
    issn_online = Column('issn_online', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'title', 'med_abbr', 'issn_print', 'issn_online',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = self.title if self.title is not None else self.med_abbr
        self.format_name = create_format_name(self.display_name[:99] if self.med_abbr is None else self.display_name[:50] + '_' + self.med_abbr[:49])

    def unique_key(self):
        return self.title, self.med_abbr

class Reference(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'reference'

    id = Column('reference_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    sgdid = Column('sgdid', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))

    ref_status = Column('ref_status', String)
    pubmed_id = Column('pubmed_id', Integer)
    pubmed_central_id = Column('pubmed_central_id', String)
    fulltext_status = Column('fulltext_status', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', String)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer, ForeignKey(Journal.id))
    book_id = Column('book_id', Integer, ForeignKey(Book.id))
    doi = Column('doi', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())
    class_type = 'REFERENCE'
    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)
    source = relationship(Source, uselist=False, lazy='joined')

    author_names = association_proxy('author_references', 'author_name')
    related_references = association_proxy('refrels', 'child_ref')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'ref_status', 'pubmed_id',
                     'pubmed_central_id', 'fulltext_status', 'citation', 'year', 'date_published', 'date_revised',
                     'issue', 'page', 'volume', 'title', 'doi',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'journal', 'book']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = self.sgdid if self.pubmed_id is None else str(self.pubmed_id)
        self.link = '/reference/' + self.sgdid + '/overview'

    def unique_key(self):
        return self.format_name

    def to_min_json(self, include_description=False):
        obj_json = UpdateByJsonMixin.to_min_json(self, include_description=include_description)
        obj_json['pubmed_id'] = self.pubmed_id
        return obj_json

    def to_semi_json(self):
        obj_json = self.to_min_json()
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['citation'] = self.citation
        obj_json['year'] = self.year
        obj_json['journal'] = None if self.journal is None else self.journal.med_abbr
        obj_json['urls'] = [x.to_json() for x in self.urls]
        return obj_json

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['abstract'] = None if len(self.paragraphs) == 0 else self.paragraphs[0].to_json(linkit=True)
        obj_json['bibentry'] = None if self.bibentry is None else self.bibentry.text
        obj_json['reftypes'] = [x.reftype.to_min_json() for x in self.ref_reftypes]
        obj_json['authors'] = [x.author.to_min_json() for x in self.author_references]
        interaction_locus_ids = set()
        interaction_locus_ids.update([x.locus1_id for x in self.physinteraction_evidences])
        interaction_locus_ids.update([x.locus2_id for x in self.physinteraction_evidences])
        interaction_locus_ids.update([x.locus1_id for x in self.geninteraction_evidences])
        interaction_locus_ids.update([x.locus2_id for x in self.geninteraction_evidences])
        regulation_locus_ids = set()
        regulation_locus_ids.update([x.locus1_id for x in self.regulation_evidences])
        regulation_locus_ids.update([x.locus2_id for x in self.regulation_evidences])
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        obj_json['counts'] = {
            'interaction': len(interaction_locus_ids),
            'go': len(set([x.locus_id for x in self.go_evidences])),
            'phenotype': len(set([x.locus_id for x in self.phenotype_evidences])),
            'regulation': len(regulation_locus_ids)
        }
        obj_json['related_references'] = []
        for child in self.children:
            child_json = child.child.to_semi_json()
            child_json['abstract'] = None if len(child.child.paragraphs) == 0 else child.child.paragraphs[0].to_json(linkit=True)
            child_json['reftypes'] = [x.reftype.to_min_json() for x in child.child.ref_reftypes]
            obj_json['related_references'].append(child_json)
        for parent in self.parents:
            parent_json = parent.parent.to_semi_json()
            parent_json['abstract'] = None if len(parent.parent.paragraphs) == 0 else parent.parent.paragraphs[0].to_json(linkit=True)
            parent_json['reftypes'] = [x.reftype.to_min_json() for x in parent.parent.ref_reftypes]
            obj_json['related_references'].append(parent_json)
        obj_json['urls'] = [x.to_json() for x in self.urls]
        if self.journal is not None:
            obj_json['journal']['med_abbr'] = self.journal.med_abbr
        return obj_json

class Bibentry(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'bibentry'

    id = Column('reference_id', Integer, ForeignKey(Reference.id), primary_key = True)
    text = Column('text', CLOB)

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref("bibentry", uselist=False, passive_deletes=True))

    __eq_values__ = ['id', 'text']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.id

class Abstract(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'abstract'

    id = Column('reference_id', Integer, ForeignKey(Reference.id), primary_key = True)
    text = Column('text', CLOB)

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref("abstract", uselist=False, passive_deletes=True))

    __eq_values__ = ['id', 'text']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.id

class Author(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'created_by', 'date_created']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(self.display_name)
        self.link = '/author/' + self.format_name + '/overview'

    def unique_key(self):
        return self.format_name

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        references = set([x.reference for x in self.author_references])
        obj_json['references'] = [x.to_semi_json() for x in sorted(references, key=lambda x: (x.year, x.date_published), reverse=True)]
        return obj_json

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

class Reftype(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'reftype'

    id = Column('reftype_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'created_by', 'date_created']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(self.display_name)

    def unique_key(self):
        return self.format_name

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

class Referencerelation(Relation):
    __tablename__ = 'referencerelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Reference.id))
    child_id = Column('child_id', Integer, ForeignKey(Reference.id))

    #Relationships
    parent = relationship(Reference, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Reference, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'parent', 'child']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))

class Referenceurl(Url):
    __tablename__ = 'referenceurl'

    id = Column('url_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))

    #Relationships
    reference = relationship(Reference, backref=backref('urls', passive_deletes=True), uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == Url.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'reference_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('reference_id'))

class Referencealias(Alias):
    __tablename__ = 'referencealias'

    id = Column('alias_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))

    #Relationships
    reference = relationship(Reference, backref=backref('aliases', passive_deletes=True), uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == Alias.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'reference_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name =str(obj_json.get('reference_id'))



