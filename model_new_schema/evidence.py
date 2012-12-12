'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, CommonEqualityMixin
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String

class Evidence(Base, CommonEqualityMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey('experiment.exp_id'))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.ref_id'))
    type = Column('evidence_type', String)
    
    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity':"EVIDENCE"}
    
    experiment = relationship('Experiment')
    reference = relationship('Reference')
    
    def __init__(self, experiment, reference):
        self.experiment = experiment
        self.reference = reference
    
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
        
class Experiment(Base, CommonEqualityMixin):
    __tablename__ = "experiment"
    
    id = Column('exp_id', Integer, primary_key=True)
    type = Column('exp_type', String)
    scale = Column('scale', String)
    modification = Column('modification', String)
    
    def __init__(self, exp_type, scale, modification):
        self.type = exp_type
        self.scale = scale
        self.modification = modification
    
    def __repr__(self):
        data = self.__class__.__name__, self.id
        return '%s(id=%s)' % data
    
class Reference(Base, CommonEqualityMixin):
    __tablename__ = "reference"
    
    id = Column('ref_id', Integer, primary_key=True)
    source = Column('source', String)
    status = Column('status', String)
    pdf_status = Column('pdf_status', String)
    dbxref_id = Column('dbxref_id', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed = Column('pubmed', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_recised', Integer)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer)
    book_id = Column('book_id', Integer)
    
    def __init__(self, source, status, pdf_status, dbxref_id, citation, year, pubmed, date_published, date_revised, issue, page, volume, title, journal_id, book_id):
        self.source = source
        self.status = status
        self.pdf_status = pdf_status
        self.dbxref_id = dbxref_id
        self.citation = citation
        self.year = year
        self.pubmed = pubmed
        self.date_published = date_published
        self.date_revised = date_revised
        self.issue = issue
        self.page = page
        self.volume = volume
        self.title = title
        self.journal_id = journal_id
        self.book_id = book_id
    
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

    
    