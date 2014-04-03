from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB

from misc import Url, Alias, Relation
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name


__author__ = 'kpaskov'

class Book(Base, EqualityByIDMixin):
    __tablename__ = 'book'

    id = Column('book_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
                
    def __init__(self, book_id, source, title, volume_title, isbn, total_pages, publisher, publisher_location, date_created, created_by):
        self.id = book_id
        self.display_name = title
        self.format_name = create_format_name(title + '' if volume_title is None else ('_' + volume_title))
        self.obj_url = None
        self.source_id = source.id
        self.title = title
        self.volume_title = volume_title
        self.isbn = isbn
        self.total_pages = total_pages
        self.publisher = publisher
        self.publisher_location = publisher_location
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.title, self.volume_title)
    
class Journal(Base, EqualityByIDMixin):
    __tablename__ = 'journal'

    id = Column('journal_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    title = Column('title', String)
    med_abbr = Column('med_abbr', String)
    issn_print = Column('issn_print', String)
    issn_online = Column('issn_online', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, journal_id, source, title, med_abbr, issn_print, issn_online, date_created, created_by):
        self.id = journal_id
        self.display_name = title if title is not None else med_abbr
        self.format_name = create_format_name(self.display_name[:99] if med_abbr is None else self.display_name[:50] + '_' + med_abbr[:49])
        self.obj_url = None
        self.source_id = source.id
        self.title = title
        self.med_abbr = med_abbr
        self.issn_print =issn_print
        self.issn_online = issn_online
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return (self.title, self.med_abbr)

class Reference(Base, EqualityByIDMixin):
    __tablename__ = 'reference'

    id = Column('reference_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    sgdid = Column('sgdid', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String)
    
    ref_status = Column('ref_status', String)
    pubmed_id = Column('pubmed_id', Integer)
    pubmed_central_id = Column('pubmed_central_id', Integer)
    fulltext_status = Column('fulltext_status', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', Date)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer, ForeignKey(Journal.id))
    book_id = Column('book_id', Integer, ForeignKey(Book.id))
    doi = Column('doi', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships  
    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)

    author_names = association_proxy('author_references', 'author_name')
    related_references = association_proxy('refrels', 'child_ref')
    
    def __init__(self, reference_id, display_name, sgdid, source_id, 
                 ref_status, pubmed_id, pubmed_central_id, fulltext_status, citation, year, date_published, date_revised, issue, page, volume, 
                 title, journal, book, doi, date_created, created_by):
        self.id = reference_id
        self.display_name = display_name
        self.format_name = sgdid if pubmed_id is None else str(pubmed_id)
        self.sgdid = sgdid
        self.link = '/reference/' + sgdid + '/overview'
        self.source_id=source_id
        self.ref_status = ref_status
        self.fulltext_status = fulltext_status
        self.citation = citation
        self.year = year
        self.date_published = date_published
        self.date_revised = date_revised
        self.issue = issue
        self.page = page
        self.volume = volume
        self.title = title
        self.journal_id = None if journal is None else journal.id
        self.book_id = None if book is None else book.id
        self.pubmed_id = pubmed_id
        self.pubmed_central_id = pubmed_central_id
        self.doi = doi
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name

    def to_min_json(self):
        return {
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            'id': self.id,
            }

    def to_semi_json(self):
        urls = []
        if self.pubmed_id is not None:
            urls.append({'display_name': 'PubMed', 'link': 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(self.pubmed_id)})
        if self.doi is not None:
            urls.append({'display_name': 'Full-Text', 'link': 'http://dx.doi.org/' + self.doi})
        if self.pubmed_central_id is not None:
            urls.append({'display_name': 'PMC', 'link': 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(self.pubmed_central_id)})

        obj_json = self.to_min_json()
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['citation'] = self.citation
        obj_json['year'] = self.year
        obj_json['journal'] = None if self.journal is None else self.journal.med_abbr
        obj_json['urls'] = urls
        return obj_json

    def to_json(self):
        obj_json = self.to_semi_json()
        obj_json['abstract'] = None if self.abstract is None else self.abstract.text
        obj_json['bibentry'] = None if self.bibentry is None else self.bibentry.text
        obj_json['reftypes'] = [x.reftype.display_name for x in self.ref_reftypes]
        obj_json['authors'] = [x.author.to_json() for x in self.author_references]
        obj_json['counts'] = {
            'interaction': len([x for x in self.bioentity_references if x.class_type == 'PHYSINTERACTION' or x.class_type == 'GENINTERACTION']),
            'go': len([x for x in self.bioentity_references if x.class_type == 'GO']),
            'phenotype': len([x for x in self.bioentity_references if x.class_type == 'PHENOTYPE']),
            'regulation': len([x for x in self.bioentity_references if x.class_type == 'REGULATION'])
        }
        obj_json['related_references'] = []
        for child in self.children:
            child_json = child.to_json()
            child_json['abstract'] = None if child.abstract is None else child.abstract.text
            child_json['reftypes'] = [x.reftype.display_name for x in child.ref_reftypes]
            obj_json['related_references'].append(child_json)
        for parent in self.children:
            parent_json = parent.to_json()
            parent_json['abstract'] = None if parent.abstract is None else parent.abstract.text
            parent_json['reftypes'] = [x.reftype.display_name for x in parent.ref_reftypes]
            obj_json['related_references'].append(parent_json)
        return obj_json
            
    @hybrid_property
    def authors(self):
        sorted_author_refs = sorted(list(self.author_references), key=lambda x: x.order)
        return [author_ref.author for author_ref in sorted_author_refs]   
    
    @hybrid_property
    def related_ref_str(self):
        return ', '.join([ref.name_with_link for ref in self.related_references])
    
class Bibentry(Base, EqualityByIDMixin):
    __tablename__ = 'bibentry'

    id = Column('reference_id', Integer, ForeignKey(Reference.id), primary_key = True)
    text = Column('text', CLOB)

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref("bibentry", uselist=False, passive_deletes=True))
        
    def __init__(self, reference_id, text):
        self.id = reference_id
        self.text = text
        
    def unique_key(self):
        return self.id
    
class Abstract(Base, EqualityByIDMixin):
    __tablename__ = 'abstract'

    id = Column('reference_id', Integer, ForeignKey(Reference.id), primary_key = True)
    text = Column('text', CLOB)
    
    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref("abstract", uselist=False, passive_deletes=True))
        
    def __init__(self, reference_id, text):
        self.id = reference_id
        self.text = text
        
    def unique_key(self):
        return self.id
    
class Author(Base, EqualityByIDMixin):
    __tablename__ = 'author'

    id = Column('author_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
        
    def __init__(self, author_id, display_name, source, date_created, created_by):
        self.id = author_id
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.link = '/author/' + self.format_name + '/overview'
        self.source_id = source.id
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return self.format_name
    
    @hybrid_property
    def references(self):
        sorted_references = sorted([author_ref.reference for author_ref in self.author_references], key=lambda x: x.date_published, reverse=True)
        return sorted_references

    def to_json(self):
        return {
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            'id': self.id
        }

class AuthorReference(Base, EqualityByIDMixin):
    __tablename__ = 'author_reference'
    
    id = Column('author_reference_id', Integer, primary_key = True)
    source_id = Column('source_id', Integer)
    author_id = Column('author_id', Integer, ForeignKey(Author.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    order = Column('author_order', Integer)
    author_type = Column('author_type', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    author = relationship(Author, backref=backref('author_references', passive_deletes=True), uselist=False) 
    reference = relationship(Reference, backref=backref('author_references', passive_deletes=True, order_by=order), uselist=False)
    author_name = association_proxy('author', 'display_name')
        
    def __init__(self, author_reference_id, source, author, reference, order, author_type, date_created, created_by):
        self.id = author_reference_id
        self.source_id = source.id
        self.author_id = author.id
        self.reference_id = reference.id
        self.order = order
        self.author_type = author_type
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.author_id, self.reference_id, self.order)
    
class Reftype(Base, EqualityByIDMixin):
    __tablename__ = 'reftype'

    id = Column('reftype_id', Integer, primary_key = True)
    source_id = Column('source_id', String)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, reftype_id, display_name, source, date_created, created_by):
        self.id = reftype_id
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.link = None
        self.source_id = source.id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
class ReferenceReftype(Base, EqualityByIDMixin):
    __tablename__ = 'reference_reftype'

    id = Column('reference_reftype_id', Integer, primary_key = True)
    source_id = Column('source_id', String)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    reftype_id = Column('reftype_id', Integer, ForeignKey(Reftype.id))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    #Relationships
    reference = relationship(Reference, backref=backref('ref_reftypes', passive_deletes=True), uselist=False)
    reftype = relationship(Reftype, backref=backref('ref_reftypes', passive_deletes=True), uselist=False)
    
    def __init__(self, reference_reftype_id, source, reference, reftype, date_created, created_by):
        self.id = reference_reftype_id
        self.source_id = source.id
        self.reference_id = reference.id
        self.reftype_id = reftype.id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.reference_id, self.reftype_id)
    
class Referencerelation(Relation):
    __tablename__ = 'referencerelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Reference.id))
    child_id = Column('child_id', Integer, ForeignKey(Reference.id))

    #Relationships
    parent = relationship(Reference, backref="children", uselist=False, foreign_keys=[parent_id])
    child = relationship(Reference, backref="parents", uselist=False, foreign_keys=[child_id])
    
    __mapper_args__ = {'polymorphic_identity': 'REFERENCE',
                       'inherit_condition': id == Relation.id}
   
    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self, parent.format_name + '_' + child.format_name, 
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name, 
                          'REFERENCE', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id
    
class Referenceurl(Url):
    __tablename__ = 'referenceurl'
    
    id = Column('url_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
        
    __mapper_args__ = {'polymorphic_identity': 'REFERENCE',
                       'inherit_condition': id == Url.id}
    
    def __init__(self, display_name, link, source, category, reference, date_created, created_by):
        Url.__init__(self, display_name, reference.format_name, 'REFERENCE', link, source, category, 
                     date_created, created_by)
        self.reference_id = reference.id
    
class Referencealias(Alias):
    __tablename__ = 'referencealias'
    
    id = Column('alias_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, reference, date_created, created_by):
        Alias.__init__(self, display_name, reference.format_name, 'REFERENCE', None, source, category, date_created, created_by)
        self.reference_id = reference.id
 


