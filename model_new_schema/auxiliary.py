'''
Created on Aug 8, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.reference import Reference
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Biofact(Base, EqualityByIDMixin):
    __tablename__ = 'aux_biofact'

    id = Column('biofact_id', Integer, primary_key=True)
    bioentity_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id))
    class_type = Column('class', String)
    
    def __init__(self, bioentity_id, bioconcept_id, class_type):
        self.bioentity_id = bioentity_id
        self.bioconcept_id = bioconcept_id
        self.class_type = class_type

    def unique_key(self):
        return (self.bioentity_id, self.bioconcept_id, self.class_type)
    
class Interaction(Base, EqualityByIDMixin):
    __tablename__ = "aux_interaction"
    
    id = Column('interaction_id', Integer, primary_key = True)
    class_type = Column('class', String)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    bioentity1_id = Column('bioentity1_id', Integer)
    bioentity2_id = Column('bioentity2_id', Integer)
    evidence_count = Column('evidence_count', Integer)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"INTERACTION"}
    
    def __init__(self, interaction_id, class_type, display_name, format_name, bioentity1_id, bioentity2_id):
        self.id = interaction_id
        self.class_type = class_type
        self.display_name = display_name
        self.format_name = format_name
        self.bioentity1_id = bioentity1_id
        self.bioentity2_id = bioentity2_id
        
    def unique_key(self):
        return (self.format_name, self.class_type)
    
class Geninteraction(Interaction, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'GENINTERACTION',
                       'inherit_condition': id==Interaction.id}

class Physinteraction(Interaction, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'PHYSINTERACTION',
                       'inherit_condition': id==Interaction.id}
    
class Reginteraction(Interaction, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'REGULATION',
                       'inherit_condition': id==Interaction.id}
    
class InteractionFamily(Base, EqualityByIDMixin):
    __tablename__ = "aux_interaction_family"
    
    id = Column('interaction_family_id', Integer, primary_key = True)
    bioentity_id = Column('bioentity_id', Integer)
    bioentity1_id = Column('bioentity1_id', Integer)
    bioentity2_id = Column('bioentity2_id', Integer)
    evidence_count = Column('evidence_count', Integer)
    genetic_ev_count = Column('gen_ev_count', Integer)
    physical_ev_count = Column('phys_ev_count', Integer)
    
    def __init__(self, bioentity_id, bioentity1_id, bioentity2_id, 
                 genetic_ev_count, physical_ev_count, evidence_count):
        self.bioentity_id = bioentity_id
        self.bioentity1_id = bioentity1_id
        self.bioentity2_id = bioentity2_id
        self.genetic_ev_count = genetic_ev_count
        self.physical_ev_count = physical_ev_count
        self.evidence_count = evidence_count
        
    def unique_key(self):
        return (self.bioentity_id, self.bioentity1_id, self.bioentity2_id)
    
class RegulationFamily(Base, EqualityByIDMixin):
    __tablename__ = "aux_regulation_family"
    
    id = Column('regulation_family_id', Integer, primary_key = True)
    bioentity_id = Column('bioentity_id', Integer)
    bioentity1_id = Column('bioentity1_id', Integer)
    bioentity2_id = Column('bioentity2_id', Integer)
    evidence_count = Column('evidence_count', Integer)
    
    def __init__(self, bioentity_id, bioentity1_id, bioentity2_id, 
                 evidence_count):
        self.bioentity_id = bioentity_id
        self.bioentity1_id = bioentity1_id
        self.bioentity2_id = bioentity2_id
        self.evidence_count = evidence_count
        
    def unique_key(self):
        return (self.bioentity_id, self.bioentity1_id, self.bioentity2_id)

class BioconceptAncestor(Base, EqualityByIDMixin):
    __tablename__ = 'aux_bioconcept_ancestor'

    id = Column('bioconcept_ancestor_id', Integer, primary_key=True)
    ancestor_bioconcept_id = Column('ancestor_bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    child_bioconcept_id = Column('child_bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    generation = Column('generation', Integer)
    class_type = Column('class', String)
    
    ancestor_bioconcept = relationship('Bioconcept', uselist=False, backref=backref('child_family', cascade='all,delete'), primaryjoin="BioconceptAncestor.ancestor_bioconcept_id==Bioconcept.id")
    child_bioconcept = relationship('Bioconcept', uselist=False, backref=backref('parent_family', cascade='all,delete'), primaryjoin="BioconceptAncestor.child_bioconcept_id==Bioconcept.id")
   
    def __init__(self, ancestor_bioconcept_id, child_bioconcept_id, class_type, generation):
        self.ancestor_bioconcept_id = ancestor_bioconcept_id
        self.child_bioconcept_id = child_bioconcept_id
        self.class_type = class_type
        self.generation = generation

    def unique_key(self):
        return (self.ancestor_bioconcept_id, self.child_bioconcept_id, self.class_type)

class BioentityReference(Base):
    __tablename__ = 'aux_bioentity_reference'
    
    id = Column('bioentity_reference_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('class', String)
    
    def __init__(self, class_type, bioentity_id, reference_id):
        self.class_type = class_type
        self.bioentity_id = bioentity_id
        self.reference_id = reference_id
        
    def unique_key(self):
        return (self.bioentity_id, self.reference_id, self.class_type)
    
class GeninteractionBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'GENINTERACTION',
                       'inherit_condition': id==BioentityReference.id}
    
class PhysinteractionBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'PHYSINTERACTION',
                       'inherit_condition': id==BioentityReference.id}
    
class GoBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'GO',
                       'inherit_condition': id==BioentityReference.id}

class PhenotypeBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'PHENOTYPE',
                       'inherit_condition': id==BioentityReference.id}
    
class RegulationBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'REGULATION',
                       'inherit_condition': id==BioentityReference.id}   
    
class PrimaryBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'PRIMARY_LITERATURE',
                       'inherit_condition': id==BioentityReference.id} 
    
class AdditionalBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'ADDITIONAL_LITERATURE',
                       'inherit_condition': id==BioentityReference.id} 

class ReviewBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'REVIEW_LITERATURE',
                       'inherit_condition': id==BioentityReference.id} 

class OmicsBioentityReference(BioentityReference, EqualityByIDMixin):
    __mapper_args__ = {'polymorphic_identity': 'OMICS_LITERATURE',
                       'inherit_condition': id==BioentityReference.id} 
    
    