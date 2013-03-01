'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.reference import Reference
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    experiment_type = Column('experiment_type', String)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    evidence_type = Column('evidence_type', String)
    strain_id = Column('strain_id', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': evidence_type,
                       'polymorphic_identity':"EVIDENCE",
                       'with_polymorphic':'*'}
    
    #Relationships
    reference = relationship('Reference', backref='evidences', uselist=False)
    
    def __init__(self, experiment_type, reference_id, evidence_type, strain_id, session=None, evidence_id=None, date_created=None, created_by=None):
        self.experiment_type = experiment_type
        self.experiment_type = experiment_type
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
    source = Column('source', String)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    note = Column('note', String)
    annotation_type = Column('annotation_type', String)
    modification = Column('modification', String)
    direction = Column('direction', String)
    interaction_type = Column('interaction_type', String)
    
    __mapper_args__ = {'polymorphic_identity': "INTERACTION_EVIDENCE"}
    
    biorel = association_proxy('biorel_evidence', 'biorel')

    
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
    name = Column('name', String)
    parent_id = Column('parent_bioent_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    description = Column('description', String)
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    #Relationships
    parent = relationship('Bioentity')
        
class Phenoevidence(Evidence):
    __tablename__ = "phenoevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    mutant_type = Column('mutant_type', String)
    mutant_allele_id = Column('mutant_allele', Integer, ForeignKey('sprout.allele.allele_id'))
    source = Column('source', String)
    experiment_comment = Column('experiment_comment', String)
    qualifier = Column('qualifier', String)
    
    #chemical = Column('chemical', String)
    #chemical_amt = Column('chemical_amt', String)
    #reporter = Column('reporter', String)
    #reporter_desc = Column('reporter_desc', String)
    #strain_details = Column('strain_details', String)
    #budding_index = Column('budding_index', String)
    #glutathione_excretion = Column('glutathione_excretion', String)
    #z_score = Column('z_score', String)
    #relative_fitness_score = Column('relative_fitness_score', String)
    #chitin_level = Column('chitin_level', String)
    #condition = Column('condition', String)
    #condition_desc = Column('condition_desc', String)
    #details = Column('details', String)
    #details_desc = Column('details_desc', String)
    
    
    #Relationship
    mutant_allele = relationship('Allele', lazy='subquery')
    bioent_biocon = association_proxy('bioent_biocon_evidence', 'bioent_biocon')
    
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE_EVIDENCE"}

    
    def __init__(self, experiment_type, reference_id, strain_id, mutant_type, mutant_allele_id, source, experiment_comment, qualifier, session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, experiment_type, reference_id, 'PHENOTYPE_EVIDENCE', strain_id, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.mutant_type = mutant_type
        self.mutant_allele_id = mutant_allele_id
        self.source = source
        self.experiment_comment = experiment_comment
        self.qualifier = qualifier
        
#class Chemevidence(Evidence):
    #__tablename__ = "chemevidence"
    
    #id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    #chemevidence_type = Column('chemevidence_type', String)
    #qualifier = Column('qualifier', String)

    
    #mutant_type = Column('mutant_type', String)
    #mutant_allele_id = Column('mutant_allele', Integer, ForeignKey('sprout.allele.allele_id'))
    #source = Column('source', String)
    #experiment_comment = Column('experiment_comment', String)
    
    #chemical = Column('chemical', String)
    #chemical_amt = Column('chemical_amt', String)
    #reporter = Column('reporter', String)
    #reporter_desc = Column('reporter_desc', String)
    #strain_details = Column('strain_details', String)
    #budding_index = Column('budding_index', String)
    #glutathione_excretion = Column('glutathione_excretion', String)
    #z_score = Column('z_score', String)
    #relative_fitness_score = Column('relative_fitness_score', String)
    #chitin_level = Column('chitin_level', String)
    #condition = Column('condition', String)
    #condition_desc = Column('condition_desc', String)
    #details = Column('details', String)
    #details_desc = Column('details_desc', String)
    
    
    #Relationship
    #mutant_allele = relationship('Allele', lazy='subquery')
    #bioent_biocon = association_proxy('bioent_biocon_evidence', 'bioent_biocon')
    
    #__mapper_args__ = {'polymorphic_identity': "CHEMICAL_EVIDENCE"}

    
    #def __init__(self, experiment_type, reference_id, strain_id, mutant_type, mutant_allele_id, source, experiment_comment, qualifier,
    #             chemevidence_type, 
    #             session=None, evidence_id=None, date_created=None, created_by=None):
    #    Evidence.__init__(self, experiment_type, reference_id, 'CHEMICAL_EVIDENCE', strain_id, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
    #    self.mutant_type = mutant_type
    #    self.mutant_allele_id = mutant_allele_id
    #    self.source = source
    #    self.experiment_comment = experiment_comment
    #    self.qualifier = qualifier
    #    self.chemevidence_type = chemevidence_type
        