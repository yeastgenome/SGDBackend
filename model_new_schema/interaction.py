'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from model_new_schema.phenotype import Phenotype
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Interaction(Base, EqualityByIDMixin):
    __tablename__ = "interaction"
    
    id = Column('interaction_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    interaction_type = Column('interaction_type', String)
    bioent1_id = Column('bioent1_id', Integer)
    bioent2_id = Column('bioent2_id', Integer)
    bioent1_name_with_link = Column('bioent1_name_with_link', String)
    bioent2_name_with_link = Column('bioent2_name_with_link', String)
    evidence_count = Column('evidence_count', Integer)
    type = 'INTERACTION'
    
    def __init__(self, interaction_id, display_name, format_name, interaction_type, bioent1_id, bioent2_id, 
                 bioent1_name_with_link, bioent2_name_with_link):
        self.id = interaction_id
        self.display_name = display_name
        self.format_name = format_name
        self.bioent1_id = bioent1_id
        self.bioent2_id = bioent2_id
        self.bioent1_name_with_link = bioent1_name_with_link
        self.bioent2_name_with_link = bioent2_name_with_link
        self.interaction_type = interaction_type
        
    def unique_key(self):
        return (self.format_name, self.interaction_type)
    
    @hybrid_property
    def endpoint_name_with_links(self):
        return self.bioent1_name_with_link, self.bioent2_name_with_link
    
class InteractionFamily(Base, EqualityByIDMixin):
    __tablename__ = "interaction_family"
    
    id = Column('interaction_family_id', Integer, primary_key = True)
    bioent_id = Column('bioent_id', Integer)
    bioent1_id = Column('bioent1_id', Integer)
    bioent2_id = Column('bioent2_id', Integer)
    bioent1_display_name = Column('bioent1_display_name', String)
    bioent2_display_name = Column('bioent2_display_name', String)
    bioent1_link = Column('bioent1_link', String)
    bioent2_link = Column('bioent2_link', String)
    evidence_count = Column('evidence_count', Integer)
    
    def __init__(self, bioent_id, bioent1_id, bioent2_id, 
                 bioent1_display_name, bioent2_display_name, bioent1_link, bioent2_link, evidence_count):
        self.bioent_id = bioent_id
        self.bioent1_id = bioent1_id
        self.bioent2_id = bioent2_id
        self.bioent1_display_name = bioent1_display_name
        self.bioent2_display_name = bioent2_display_name
        self.bioent1_link = bioent1_link
        self.bioent2_link = bioent2_link
        self.evidence_count = evidence_count
        
    def unique_key(self):
        return (self.bioent_id, self.bioent1_id, self.bioent2_id)

class GeneticInterevidence(Evidence):
    __tablename__ = "geneticinterevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    phenotype_name_with_link = Column('phenotype_name_with_link', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioent1_id = Column('bioent1_id', Integer, ForeignKey(Bioentity.id))
    bioent2_id = Column('bioent2_id', Integer, ForeignKey(Bioentity.id))
    bioent1_name_with_link = Column('bioent1_name_with_link', String)
    bioent2_name_with_link = Column('bioent2_name_with_link', String)
    note = Column('note', String)
       
    __mapper_args__ = {'polymorphic_identity': "GENETIC_INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    phenotype = relationship(Phenotype)

    def __init__(self, evidence_id, 
                 experiment_id, experiment_name_with_link,
                 reference_id, reference_name_with_link, reference_citation,
                 strain_id, strain_name_with_link,
                 annotation_type, source, 
                 bioent1_id, bioent2_id, bioent1_name_with_link, bioent2_name_with_link,
                 phenotype_id, phenotype_name_with_link, 
                 bait_hit, note, date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_id, experiment_name_with_link,
                          reference_id, reference_name_with_link, reference_citation,
                          strain_id, strain_name_with_link,
                          source, 'GENETIC_INTERACTION_EVIDENCE', date_created, created_by)
        self.annotation_type = annotation_type
        self.phenotype_id = phenotype_id
        self.phenotype_name_with_link = phenotype_name_with_link
        self.bait_hit = bait_hit
        self.note = note
        self.bioent1_id = bioent1_id
        self.bioent2_id = bioent2_id
        self.bioent1_name_with_link = bioent1_name_with_link
        self.bioent2_name_with_link = bioent2_name_with_link
        
class PhysicalInterevidence(Evidence):
    __tablename__ = "physicalinterevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioent1_id = Column('bioent1_id', Integer, ForeignKey(Bioentity.id))
    bioent2_id = Column('bioent2_id', Integer, ForeignKey(Bioentity.id))
    bioent1_name_with_link = Column('bioent1_name_with_link', String)
    bioent2_name_with_link = Column('bioent2_name_with_link', String)
    note = Column('note', String)
            
    __mapper_args__ = {'polymorphic_identity': "PHYSICAL_INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
        
    def __init__(self, evidence_id, experiment_id, experiment_name_with_link,
                 reference_id, reference_name_with_link, reference_citation,
                 strain_id, strain_name_with_link,
                 annotation_type, source, 
                 bioent1_id, bioent2_id, bioent1_name_with_link, bioent2_name_with_link,
                 modification, bait_hit, note, date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_id, experiment_name_with_link,
                          reference_id, reference_name_with_link, reference_citation,
                          strain_id, strain_name_with_link,
                          source, 'PHYSICAL_INTERACTION_EVIDENCE', date_created, created_by)
        self.annotation_type = annotation_type
        self.modification = modification
        self.bait_hit = bait_hit
        self.note = note
        self.bioent1_id = bioent1_id
        self.bioent2_id = bioent2_id
        self.bioent1_name_with_link = bioent1_name_with_link
        self.bioent2_name_with_link = bioent2_name_with_link
        
        
        