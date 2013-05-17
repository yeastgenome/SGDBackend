'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema import SCHEMA, Base
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Biofact
from model_new_schema.evidence import Evidence
from model_new_schema.misc import Chemical
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Float


class Phenotype(Bioconcept):
    __tablename__ = "phenotype"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
    phenotype_type = Column('phenotype_type', String)
    direct_gene_count = Column('direct_gene_count', Integer)
    type = "PHENOTYPE"
    
    @hybrid_property
    def search_entry_type(self):
        return 'Phenotype'
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, observable, phenotype_type, description, session=None, biocon_id=None, date_created=None, created_by=None):
        name = observable.replace(' ', '_')
        name = name.replace('/', '-')
        Bioconcept.__init__(self, 'PHENOTYPE', name, description, session=session, biocon_id=biocon_id, date_created=date_created, created_by=created_by)
        self.observable = str(observable)
        self.phenotype_type = phenotype_type
         
        
    @classmethod
    def unique_hash(cls, qualifier, observable):
        return '%s_%s' % (qualifier, observable) 

    @classmethod
    def unique_filter(cls, query, qualifier, observable):
        return query.filter(Phenotype.qualifier == qualifier, Phenotype.observable == observable)
  
class PhenoevidenceChemical(Base):
    __tablename__ = 'phenoevidence_chemical'
    id = Column('phenoevidence_chemical_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey('sprout.phenoevidence.evidence_id'))
    chemical_id = Column('chemical_id', Integer, ForeignKey('sprout.chemical.chemical_id'))
    chemical_amt = Column('chemical_amount', String)
    
    def __init__(self, evidence_id, chemical_id, chemical_amt):
        self.evidence_id = evidence_id
        self.chemical_id = chemical_id
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
    details = Column('details', String)
    experiment_details = Column('experiment_details', String)
    conditions = Column('conditions', String)
    
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    biocon_id = Column('biocon_id', Integer, ForeignKey(Phenotype.id))
    
    type = 'BIOCON_EVIDENCE'
    
    #Relationship
    bioentity = relationship(Bioentity)
    phenotype = relationship(Phenotype)
    
    
    allele = relationship('Allele', lazy='subquery', uselist=False)
    phenoev_chemicals = relationship('PhenoevidenceChemical', backref='evidence', lazy='joined')
    chemicals = association_proxy('phenoev_chemicals', 'chemical')

    
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    


    
    def __init__(self, experiment_type, reference_id, strain_id, mutant_type, mutant_allele_id, source, 
                 qualifier,
                 bioent_biocon_id, evidence_type='PHENOTYPE_EVIDENCE', session=None, evidence_id=None, date_created=None, created_by=None):
        Evidence.__init__(self, experiment_type, reference_id, evidence_type, strain_id, session=session, evidence_id=evidence_id, date_created=date_created, created_by=created_by)
        self.mutant_type = mutant_type
        self.mutant_allele_id = mutant_allele_id
        self.source = source
        self.qualifier = qualifier
        self.bioent_biocon_id = bioent_biocon_id