'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from model_new_schema.phenotype import Phenotype
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

class Geninteractionevidence(Evidence):
    __tablename__ = "geninteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
       
    __mapper_args__ = {'polymorphic_identity': "GENINTERACTION",
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    phenotype = relationship(Phenotype)

    def __init__(self, evidence_id, experiment_id, reference_id, strain_id, source_id, 
                 bioentity1_id, bioentity2_id, phenotype_id, annotation_type, bait_hit, note, 
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, 'GENINTERACTION', 
                          experiment_id, reference_id, strain_id, source_id, note,
                          date_created, created_by)
        self.bioentity1_id = bioentity1_id
        self.bioentity2_id = bioentity2_id
        self.phenotype_id = phenotype_id
        self.annotation_type = annotation_type
        self.bait_hit = bait_hit
        self.note = note
        
class Physinteractionevidence(Evidence):
    __tablename__ = "physinteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
            
    __mapper_args__ = {'polymorphic_identity': "PHYSINTERACTION",
                       'inherit_condition': id==Evidence.id}
    
        
    def __init__(self, evidence_id, experiment_id, reference_id, strain_id, source_id,
                 bioentity1_id, bioentity2_id, annotation_type, modification, bait_hit, note, 
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, 'PHYSINTERACTION', 
                          experiment_id, reference_id, strain_id, source_id, note,
                          date_created, created_by)
        self.bioentity1_id = bioentity1_id
        self.bioentity2_id = bioentity2_id
        self.annotation_type = annotation_type
        self.modification = modification
        self.bait_hit = bait_hit
        self.note = note

        
        
        