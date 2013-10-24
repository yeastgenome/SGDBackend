'''
Created on Aug 8, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.reference import Reference
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Biofact(Base, EqualityByIDMixin):
    __tablename__ = 'aux_biofact'

    id = Column('aux_biofact_id', Integer, primary_key=True)
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
    
    id = Column('aux_interaction_id', Integer, primary_key = True)
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

class BioentityReference(Base):
    __tablename__ = 'aux_bioentity_reference'
    
    id = Column('aux_bioentity_reference_id', Integer, primary_key=True)
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
    
class Disambig(Base, EqualityByIDMixin):
    __tablename__ = 'aux_disambig'
    
    id = Column('aux_disambig_id', Integer, primary_key=True)
    disambig_key = Column('disambig_key', String)
    class_type = Column('class_type', String)
    subclass_type = Column('subclass_type', String)
    identifier = Column('obj_id', String)
    
    def __init__(self, disambig_key, class_type, subclass_type, identifier):
        self.disambig_key = disambig_key
        self.class_type = class_type
        self.subclass_type = subclass_type
        self.identifier = identifier
        
    def unique_key(self):
        return (self.disambig_key, self.class_type, self.subclass_type)
    
class Locustabs(Base, EqualityByIDMixin):
    __tablename__ = 'aux_locustabs'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    summary = Column('summary', Integer)
    history = Column('history', Integer)
    literature = Column('literature', Integer)
    go = Column('go', Integer)
    phenotype = Column('phenotype', Integer)
    interactions = Column('interactions', Integer)
    expression = Column('expression', Integer)
    regulation = Column('regulation', Integer)
    protein = Column('protein', Integer)
    wiki = Column('wiki', Integer)
            
    def __init__(self, bioentity_id, show_summary, show_history, show_literature, show_go, show_phenotype, 
                 show_interactions, show_expression, show_regulation, show_protein, show_wiki):
        self.id = bioentity_id
        self.summary = show_summary
        self.history = show_history
        self.literature = show_literature
        self.go = show_go
        self.phenotype = show_phenotype
        self.interactions = show_interactions
        self.expression = show_expression
        self.regulation = show_regulation
        self.protein = show_protein
        self.wiki = show_wiki
            
    def unique_key(self):
        return self.id
    