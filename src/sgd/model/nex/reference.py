from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from misc import Url, Alias, Relation
from src.sgd.model.nex.basic import Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name
from src.sgd.model.nex.basic import BasicObject, UpdateByJsonMixin
__author__ = 'kpaskov'


class Reference(BasicObject):
    __tablename__ = 'reference'

    id = Column('id', Integer, ForeignKey(BasicObject.id), primary_key=True)

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
    basicobjects = association_proxy('reference_basicobjects', 'basicobject')

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == BasicObject.id}
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

