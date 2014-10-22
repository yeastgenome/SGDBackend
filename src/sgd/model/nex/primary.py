__author__ = 'kpaskov'

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model.nex import Base, BasicObject, create_format_name, UpdateByJsonMixin


class Primary(Base, BasicObject):
    __tablename__ = 'primaryobject'

    id = Column('id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    budid = Column('budid', Integer)
    sgdid = Column('sgdid', String)
    status = Column('status', String)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    tags = association_proxy('primary_tags', 'tag')

    __mapper_args__ = {'polymorphic_on': class_type}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type']
    __fks__ = ['source', 'urls', 'aliases', 'relations', 'qualities', 'tags', 'paragraphs']

    def unique_key(self):
        return self.class_type, self.format_name


class Locus(Primary):
    __tablename__ = "locus"

    id = Column('id', Integer, ForeignKey(Primary.id), primary_key=True)
    uniprotid = Column('uniprotid', String)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    locus_type = Column('locus_type', String)
    gene_name = Column('gene_name', String)
    qualifier = Column('qualifier', String)
    genetic_position = Column('genetic_position', Integer)

    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Primary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type',
                     'uniprotid', 'name_description', 'headline', 'locus_type', 'gene_name', 'qualifier', 'genetic_position']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.link = None if self.sgdid is None else '/locus/' + self.sgdid + '/overview'


class Reference(Primary):
    __tablename__ = 'reference'

    id = Column('id', Integer, ForeignKey(Primary.id), primary_key=True)

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
    journal_id = Column('journal_id', Integer, ForeignKey('journal.id'))
    book_id = Column('book_id', Integer, ForeignKey('book.id'))
    doi = Column('doi', String)

    #Relationships
    book = relationship('Book', uselist=False)
    journal = relationship('Journal', uselist=False)

    author_names = association_proxy('author_references', 'author_name')
    related_references = association_proxy('refrels', 'child_ref')

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == Primary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type',
                'pubmed_id', 'pubmed_central_id', 'fulltext_status', 'citation', 'year', 'date_published', 'date_revised', 'issue', 'page', 'volume', 'title', 'doi']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type', 'pubmed_id', 'year']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type', 'pubmed_id', 'year', 'citation', 'journal', ]
    __fks__ = ['source', 'journal', 'book', 'urls', 'aliases', 'relations', 'qualities', 'tags', 'paragraphs']
    __semi_fks__ = ['journal', 'urls']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = self.sgdid if self.pubmed_id is None else str(self.pubmed_id)
        self.link = None if self.sgdid is None else '/reference/' + self.sgdid + '/overview'


class Strain(Primary):
    __tablename__ = 'strain'

    id = Column('id', Integer, ForeignKey(Primary.id), primary_key=True)

    genotype = Column('genotype', String)

    __mapper_args__ = {'polymorphic_identity': 'STRAIN', 'inherit_condition': id == Primary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'description', 'bud_id', 'status', 'date_created', 'created_by', 'class_type',
                'genotype']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name.replace('.', ''))
        self.link = None if self.format_name is None else '/strain/' + self.format_name + '/overview'
