from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

from bioconcept import Bioconcept
from bioentity import Bioentity
from reference import Reference
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateByJsonMixin


__author__ = 'kpaskov'

class Biofact(Base, EqualityByIDMixin):
    __tablename__ = 'aux_biofact'

    id = Column('aux_biofact_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    bioentity_class_type = Column('bioentity_subclass', String)
    bioconcept_class_type = Column('bioconcept_subclass', String)

    #Relationships
    bioconcept = relationship(Bioconcept, uselist=False)
    bioentity = relationship(Bioconcept, uselist=False)
    
    def __init__(self, bioentity, bioconcept):
        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id
        self.bioentity_class_type = bioentity.class_type
        self.bioconcept_class_type = bioconcept.class_type

    def unique_key(self):
        return (self.bioentity_id, self.bioconcept_id, self.bioentity_class_type, self.bioconcept_class_type)
    
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

    #Relationships
    bioentity = relationship(Bioentity, uselist=False)
    reference = relationship(Reference, uselist=False, backref=backref('bioentity_references', passive_deletes=True))

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
    
class Disambig(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'aux_disambig'
    
    id = Column('aux_disambig_id', Integer, primary_key=True)
    disambig_key = Column('disambig_key', String)
    class_type = Column('class', String)
    subclass_type = Column('subclass', String)
    identifier = Column('obj_id', String)

    __eq_values__ = ['id', 'disambig_key', 'class_type', 'subclass_type', 'identifier']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.disambig_key = obj_json.get('disambig_key').replace('/', '-').replace(' ', '_')
        
    def unique_key(self):
        return self.disambig_key, self.class_type, self.subclass_type
    
class Locustabs(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'aux_locustabs'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    summary_tab = Column('summary', Integer)
    sequence_tab = Column('seq', Integer)
    history_tab = Column('history', Integer)
    literature_tab = Column('literature', Integer)
    go_tab = Column('go', Integer)
    phenotype_tab = Column('phenotype', Integer)
    interaction_tab = Column('interactions', Integer)
    expression_tab = Column('expression', Integer)
    regulation_tab = Column('regulation', Integer)
    protein_tab = Column('protein', Integer)
    wiki_tab = Column('wiki', Integer)

    __eq_values__ = ['id', 'summary_tab', 'history_tab', 'literature_tab', 'go_tab', 'phenotype_tab', 'interaction_tab',
                     'expression_tab', 'regulation_tab', 'protein_tab', 'sequence_tab', 'wiki_tab']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.id

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        new_obj_json = {'id': obj_json['id']}
        for key, value in obj_json.iteritems():
            if key != 'id':
                new_obj_json[key] = value == 1
        return new_obj_json