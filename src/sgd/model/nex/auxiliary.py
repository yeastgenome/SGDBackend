from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

from bioconcept import Bioconcept
from bioentity import Bioentity
from reference import Reference
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base


__author__ = 'kpaskov'

class Biofact(Base, EqualityByIDMixin):
    __tablename__ = 'aux_biofact'

    id = Column('aux_biofact_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    bioentity_class_type = Column('bioentity_subclass', String)
    bioconcept_class_type = Column('bioconcept_subclass', String)
    
    def __init__(self, bioentity, bioconcept):
        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id
        self.bioentity_class_type = bioentity.class_type
        self.bioconcept_class_type = bioconcept.class_type

    def unique_key(self):
        return (self.bioentity_id, self.bioconcept_id, self.bioentity_class_type, self.bioconcept_class_type)
    
class BioconceptCount(Base, EqualityByIDMixin):
    __tablename__ = 'aux_bioconcept_count'

    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key=True)
    child_gene_count = Column('child_gene_count', Integer)
    genecount = Column('genecount', Integer)
    class_type = Column('subclass', String)
    
    bioconcept = relationship(Bioconcept, backref=backref("count", uselist=False, lazy="joined"))
    
    def __init__(self, bioconcept, genecount, child_gene_count):
        self.id = bioconcept.id
        self.genecount = genecount
        self.class_type = bioconcept.class_type
        self.child_gene_count = child_gene_count

    def unique_key(self):
        return self.id
    
class ChemicalCount(Base, EqualityByIDMixin):
    __tablename__ = 'aux_chemical_count'

    id = Column('chemical_id', Integer, ForeignKey(Bioconcept.id), primary_key=True)
    child_gene_count = Column('child_gene_count', Integer)
    genecount = Column('genecount', Integer)
        
    def __init__(self, chemical, genecount, child_gene_count):
        self.id = chemical.id
        self.genecount = genecount
        self.child_gene_count = child_gene_count

    def unique_key(self):
        return self.id
    
class Interaction(Base, EqualityByIDMixin):
    __tablename__ = "aux_interaction"
    
    id = Column('aux_interaction_id', Integer, primary_key = True)
    class_type = Column('bioentity_subclass', String)
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
    class_type = Column('bioentity_subclass', String)
    
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
    class_type = Column('class', String)
    subclass_type = Column('subclass', String)
    identifier = Column('obj_id', String)
    
    def __init__(self, disambig_key, class_type, subclass_type, identifier):
        self.disambig_key = disambig_key.replace('/', '-').replace(' ', '_')
        self.class_type = class_type
        self.subclass_type = subclass_type
        self.identifier = identifier
        
    def unique_key(self):
        return (self.disambig_key, self.class_type, self.subclass_type)
    
class Locustabs(Base, EqualityByIDMixin):
    __tablename__ = 'aux_locustabs'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    summary = Column('summary', Integer)
    sequence = Column('seq', Integer)
    history = Column('history', Integer)
    literature = Column('literature', Integer)
    go = Column('go', Integer)
    phenotype = Column('phenotype', Integer)
    interactions = Column('interactions', Integer)
    expression = Column('expression', Integer)
    regulation = Column('regulation', Integer)
    protein = Column('protein', Integer)
    wiki = Column('wiki', Integer)
            
    def __init__(self, bioentity_id, show_summary, show_sequence, show_history, show_literature, show_go, show_phenotype,
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
        self.sequence = show_sequence
        self.wiki = show_wiki
            
    def unique_key(self):
        return self.id
    