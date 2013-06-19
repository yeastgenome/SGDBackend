'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema.phenotype import Phenotype
from model_new_schema.bioentity import BioentMultiRelation
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class GeneticInteraction(BioentMultiRelation):
    __tablename__ = "geneticinteraction"

    id = Column('biorel_id', Integer, ForeignKey(BioentMultiRelation.id),primary_key = True)
    evidence_count = Column('evidence_count', Integer)

    __mapper_args__ = {'polymorphic_identity': "GENETIC_INTERACTION",
                       'inherit_condition': id==BioentMultiRelation.id}
    
    def __init__(self, biorel_id, display_name, format_name, date_created, created_by):
        BioentMultiRelation.__init__(self, biorel_id, display_name, format_name, 'GENETIC_INTERACTION', date_created, created_by)
        
class PhysicalInteraction(BioentMultiRelation):
    __tablename__ = "physicalinteraction"

    id = Column('biorel_id', Integer, ForeignKey(BioentMultiRelation.id),primary_key = True)
    evidence_count = Column('evidence_count', Integer)
    
    __mapper_args__ = {'polymorphic_identity': "PHYSICAL_INTERACTION",
                       'inherit_condition': id==BioentMultiRelation.id}
    
    def __init__(self, biorel_id, display_name, format_name, date_created, created_by):
        BioentMultiRelation.__init__(self, biorel_id, display_name, format_name, 'PHYSICAL_INTERACTION', date_created, created_by)
                    
    
class GeneticInterevidence(Evidence):
    __tablename__ = "geneticinterevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    biorel_id = Column('biorel_id', Integer, ForeignKey(GeneticInteraction.id))
        
    __mapper_args__ = {'polymorphic_identity': "GENETIC_INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    biorel = relationship(GeneticInteraction, backref='evidences')

    def __init__(self, evidence_id, biorel_id, experiment_id, reference_id, strain_id, annotation_type, source, phenotype_id, bait_hit, date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_id, reference_id, 'GENETIC_INTERACTION_EVIDENCE', strain_id, source, date_created, created_by)
        self.annotation_type = annotation_type
        self.phenotype_id = phenotype_id
        self.bait_hit = bait_hit
        self.biorel_id = biorel_id
        
class PhysicalInterevidence(Evidence):
    __tablename__ = "physicalinterevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    biorel_id = Column('biorel_id', Integer, ForeignKey(PhysicalInteraction.id))
        
    __mapper_args__ = {'polymorphic_identity': "PHYSICAL_INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    biorel = relationship(PhysicalInteraction, backref='evidences')
        
    def __init__(self, evidence_id, biorel_id, experiment_id, reference_id, strain_id, annotation_type, source, modification, bait_hit, date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_id, reference_id, 'PHYSICAL_INTERACTION_EVIDENCE', strain_id, source, date_created, created_by)
        self.annotation_type = annotation_type
        self.modification = modification
        self.bait_hit = bait_hit
        self.biorel_id = biorel_id
        
        
        