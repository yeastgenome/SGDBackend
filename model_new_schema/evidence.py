'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date
import datetime

class Evidence(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey('experiment.experiment_id'))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.reference_id'))
    evidence_type = Column('evidence_type', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': evidence_type,
                       'polymorphic_identity':"EVIDENCE"}
    
    #Relationships
    experiment = relationship('Experiment')
    reference = relationship('Reference')
    
    @classmethod
    def unique_hash(cls, evidence_type, experiment_id, reference_id):
        return '%s_%s_%s' % (experiment_id, reference_id, type) 

    @classmethod
    def unique_filter(cls, query, evidence_type, experiment_id, reference_id):
        return query.filter(Evidence.evidence_type == evidence_type, Evidence.experiment_id == experiment_id, Evidence.reference_id == reference_id)

    
    def __init__(self, session, experiment, reference):
        self.experiment = experiment
        self.reference = reference
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id
        return '%s(id=%s)' % data
    
class Interevidence(Evidence):
    __tablename__ = "interevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source = Column('source', String)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    note = Column('note', String)
    
    __mapper_args__ = {'polymorphic_identity': "INTEREVIDENCE"}

    
    def __init__(self, experiment, reference, source, observable, qualifier, note):
        super(Evidence, self).__init__(experiment, reference)
        self.source = source
        self.observable = observable
        self.qualifier = qualifier
        self.note = note
        
class Experiment(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "experiment"
    
    id = Column('experiment_id', Integer, primary_key=True)
    experiment_type = Column('experiment_type', String)
    scale = Column('scale', String)
    modification = Column('modification', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    
    @classmethod
    def unique_hash(cls, experiment_type, scale, modification):
        return '%s_%s_%s' % (experiment_type, scale, modification) 

    @classmethod
    def unique_filter(cls, query, experiment_type, scale, modification):
        return query.filter(Experiment.experiment_type == experiment_type, Experiment.scale == scale, Experiment.modification == modification)
        
    def __init__(self, session, exp_type, scale, modification):
        self.type = exp_type
        self.scale = scale
        self.modification = modification
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id
        return '%s(id=%s)' % data
    
class Reference(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "reference"
    
    id = Column('reference_id', Integer, primary_key=True)
    source = Column('source', String)
    status = Column('status', String)
    pdf_status = Column('pdf_status', String)
    dbxref_id = Column('dbxref_id', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed_id = Column('pubmed', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_recised', Integer)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer)
    book_id = Column('book_id', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, session, source, status, pdf_status, dbxref_id, citation, year, pubmed_id, date_published, date_revised, issue, page, volume, title, journal_id, book_id):
        self.source = source
        self.status = status
        self.pdf_status = pdf_status
        self.dbxref_id = dbxref_id
        self.citation = citation
        self.year = year
        self.pubmed_id = pubmed_id
        self.date_published = date_published
        self.date_revised = date_revised
        self.issue = issue
        self.page = page
        self.volume = volume
        self.title = title
        self.journal_id = journal_id
        self.book_id = book_id
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
        
    @classmethod
    def unique_hash(cls, pubmed_id):
        return pubmed_id

    @classmethod
    def unique_filter(cls, query, pubmed_id):
        return query.filter(Reference.pubmed_id == pubmed_id)
        
    def __repr__(self):
        data = self.__class__.__name__, self.id
        return '%s(id=%s)' % data
    
bioent_biocon_evidence_map = Table('bioent_biocon_evidence', Base.metadata,
    Column('bioent_biocon_id', Integer, ForeignKey('bioent_biocon.bioent_biocon_id')),
    Column('evidence_id', Integer, ForeignKey('evidence.evidence_id'))
)
biorel_evidence_map = Table('biorel_evidence', Base.metadata,
    Column('biorel_id', Integer, ForeignKey('biorel.biorel_id')),
    Column('evidence_id', Integer, ForeignKey('evidence.evidence_id'))
)

    
    