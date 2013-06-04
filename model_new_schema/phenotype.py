'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema import Base
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.chemical import Chemical
from model_new_schema.evidence import Evidence
from model_new_schema.misc import Allele
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Float


class Phenotype(Bioconcept):
    __tablename__ = "phenotype"
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    phenotype_type = Column('phenotype_type', String)
    direct_gene_count = Column('direct_gene_count', Integer)
    type = "PHENOTYPE"
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, biocon_id, display_name, format_name, 
                 description, phenotype_type, date_created, created_by):
        Bioconcept.__init__(self, biocon_id, 'PHENOTYPE', display_name, format_name, 
                            description, date_created, created_by)
        self.phenotype_type = phenotype_type
        
    @hybrid_property
    def search_entry_type(self):
        return 'Phenotype'
        
class Phenoevidence(Evidence):
    __tablename__ = "phenoevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    mutant_type = Column('mutant_type', String)
    mutant_allele_id = Column('mutant_allele', Integer, ForeignKey(Allele.id))
    qualifier = Column('qualifier', String)
    
    reporter = Column('reporter', String)
    reporter_desc = Column('reporter_desc', String)
    allele_info = Column('allele_info', String)
    strain_details = Column('strain_details', String)
    details = Column('details', String)
    experiment_details = Column('experiment_details', String)
    conditions = Column('conditions', String)
    
    budding_index = Column('budding_index', String)
    glutathione_excretion = Column('glutathione_excretion', String)
    z_score = Column('z_score', String)
    relative_fitness_score = Column('relative_fitness_score', Float)
    chitin_level = Column('chitin_level', Float)

    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    biocon_id = Column('biocon_id', Integer, ForeignKey(Phenotype.id))
    
    type = 'BIOCON_EVIDENCE'
    
    #Relationship
    gene = relationship(Bioentity, uselist=False)
    phenotype = relationship(Phenotype, uselist=False)
    allele = relationship(Allele, lazy='subquery', uselist=False, backref='phenoevidences')
    chemicals = association_proxy('phenoev_chemicals', 'chemical')

    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    def __init__(self, evidence_id, experiment_type, reference_id, strain_id, source,
                 mutant_type, qualifier, bioent_id, biocon_id,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_type, reference_id, 'PHENOTYPE_EVIDENCE', strain_id, source, date_created, created_by)
        self.mutant_type = mutant_type
        self.qualifier = qualifier
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id
        
class PhenoevidenceChemical(Base):
    __tablename__ = 'phenoevidence_chemical'
    
    id = Column('phenoevidence_chemical_id', Integer, primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Phenoevidence.id))
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    chemical_amt = Column('chemical_amount', String)
    
    #Relationships
    chemical = relationship(Chemical, uselist=False, lazy='joined')
    evidence = relationship(Phenoevidence, backref=backref('phenoev_chemicals', passive_deletes=True), uselist=False)
    chemical_name = association_proxy('chemical', 'display_name')
    
    def __init__(self, evidence_id, chemical_id, chemical_amt):
        self.evidence_id = evidence_id
        self.chemical_id = chemical_id
        self.chemical_amt = chemical_amt
    
    def unique_key(self):
        return (self.evidence_id, self.chemical_id)
        
        

    