'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Interaction
from model_new_schema.chemical import Chemical
from model_new_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, Float
import datetime

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    experiment_type = Column('experiment_type', String)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    evidence_type = Column('evidence_type', String)
    strain_id = Column('strain_id', String)
    source = Column('source', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': evidence_type,
                       'polymorphic_identity':"EVIDENCE",
                       'with_polymorphic':'*'}
    
    #Relationships
    reference = relationship('Reference', backref='evidences', uselist=False)
    
    def __init__(self, experiment_type, reference_id, evidence_type, strain_id, session=None, evidence_id=None, date_created=None, created_by=None):
        self.experiment_type = experiment_type
        self.reference_id = reference_id
        self.evidence_type = evidence_type
        self.strain_id = strain_id
        
        if session is None:
            self.id = evidence_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id
        return '%s(id=%s)' % data
    
class Interevidence(Evidence):
    __tablename__ = "interevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    note = Column('note', String)
    annotation_type = Column('annotation_type', String)
    modification = Column('modification', String)
    direction = Column('direction', String)
    interaction_type = Column('interaction_type', String)
    biorel_id = Column('biorel_id', Integer, ForeignKey('sprout.interaction.biorel_id'))
    
    type = 'BIOREL_EVIDENCE'
    
    __mapper_args__ = {'polymorphic_identity': "INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    biorel = relationship(Interaction, backref='evidences')

    @hybrid_property
    def phenotype(self):
        if self.qualifier is not None:
            return self.qualifier + ' ' + self.observable
        else:
            return None
        
    def __init__(self, experiment_type, reference_id, strain_id, direction, annotation_type, modification, source, observable, qualifier, note, interaction_type, session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, experiment_type, reference_id, 'INTERACTION_EVIDENCE', strain_id, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.direction = direction
        self.annotation_type = annotation_type
        self.modification = modification
        self.source = source
        self.observable = observable
        self.qualifier = qualifier
        self.note = note
        self.interaction_type = interaction_type
        
class Allele(Base):
    __tablename__ = 'allele'
    id = Column('allele_id', Integer, primary_key=True)
    official_name = Column('name', String)
    parent_id = Column('parent_bioent_id', Integer, ForeignKey('sprout.newbioent.bioent_id'))
    more_info = Column('description', String)
    
    @hybrid_property
    def name(self):
        return self.official_name
    
    @hybrid_property
    def description(self):
        return 'Allele'
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    
class PhenoevidenceChemical(Base):
    __tablename__ = 'phenoevidence_chemical'
    id = Column('phenoevidence_chemical_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey('sprout.phenoevidence.evidence_id'))
    chemical_id = Column('chemical_id', Integer, ForeignKey('sprout.chemical.chemical_id'))
    chemical_amt = Column('chemical_amount', String)
    
    def __init__(self, evidence_id, chemical_id, chemical_amt):
        self.evidence_id = evidence_id
        self.evidence_id = evidence_id
        self.chemical_amt = chemical_amt
    
    #Relationships
    chemical = relationship(Chemical, uselist=False, lazy='joined')
    chemical_name = association_proxy('chemical', 'name')
        
class Phenoevidence(Evidence):
    __tablename__ = "phenoevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    mutant_type = Column('mutant_type', String)
    mutant_allele_id = Column('mutant_allele', Integer, ForeignKey('sprout.allele.allele_id'))
    qualifier = Column('qualifier', String)
    
    reporter = Column('reporter', String)
    reporter_desc = Column('reporter_desc', String)
    strain_details = Column('strain_details', String)
    budding_index = Column('budding_index', String)
    glutathione_excretion = Column('glutathione_excretion', String)
    z_score = Column('z_score', String)
    relative_fitness_score = Column('relative_fitness_score', Float)
    chitin_level = Column('chitin_level', Float)
    description = Column('description', String)
    
    bioent_biocon_id = Column('bioent_biocon_id', Integer, ForeignKey('sprout.bioent_biocon.bioent_biocon_id'))
    
    type = 'BIOCON_EVIDENCE'
    
    #Relationship
    allele = relationship('Allele', lazy='subquery', uselist=False)
    phenoev_chemicals = relationship('PhenoevidenceChemical', backref='evidence', lazy='joined')
    chemicals = association_proxy('phenoev_chemicals', 'chemical')

    bioent_biocon = relationship(BioentBiocon)
    
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    


    
    def __init__(self, experiment_type, reference_id, strain_id, mutant_type, mutant_allele_id, source, 
                 qualifier, evidence_type='PHENOTYPE_EVIDENCE', session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, experiment_type, reference_id, evidence_type, strain_id, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.mutant_type = mutant_type
        self.mutant_allele_id = mutant_allele_id
        self.source = source
        self.qualifier = qualifier
        
class Goevidence(Evidence):
    __tablename__ = "goevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    date_last_reviewed = Column('date_last_reviewed', Date)
    qualifier = Column('qualifier', String)
    
    bioent_biocon_id = Column('bioent_biocon_id', Integer, ForeignKey(BioentBiocon.id))
    
    bioent_biocon = relationship(BioentBiocon)

    type = 'BIOCON_EVIDENCE'

    __mapper_args__ = {'polymorphic_identity': "GO_EVIDENCE",
                       'inherit_condition': id==Evidence.id}

    
    def __init__(self, bioent_biocon_id, reference_id, go_evidence, annotation_type, source, qualifier, date_last_reviewed,
                 session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, None, reference_id, 'GO_EVIDENCE', None, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.bioent_biocon_id = bioent_biocon_id
        self.go_evidence = go_evidence
        self.annotation_type = annotation_type
        self.source = source
        self.qualifier = qualifier
        self.date_last_reviewed = date_last_reviewed
        
class Bioentevidence(Evidence):
    __tablename__ = "bioentevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.newbioent.bioent_id'))
    type = 'BIOENT_EVIDENCE'
    
    bioent = relationship(Bioentity)


    __mapper_args__ = {'polymorphic_identity': "BIOENT_EVIDENCE",
                       'inherit_condition': id==Evidence.id}

    
    def __init__(self, bioent_id, reference_id, 
                 session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, None, reference_id, 'BIOENT_EVIDENCE', None, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.bioent_id = bioent_id

          
        