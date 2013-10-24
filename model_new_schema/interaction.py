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

    def __init__(self, source, reference, strain, experiment,
                 bioentity1, bioentity2, phenotype, annotation_type, bait_hit, note, 
                 date_created, created_by):
        Evidence.__init__(self, bioentity1.display_name + '__' + bioentity2.display_name,
                          bioentity1.format_name + '|' + bioentity2.format_name + '|' + ('-' if strain is None else str(strain.id)) + '|' + bait_hit + '|' + str(experiment.id) + '|' + str(reference.id), 
                          'GENINTERACTION', source, reference, strain, experiment, 
                          note, date_created, created_by)
        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.phenotype_id = None if phenotype is None else phenotype.id
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
    
        
    def __init__(self, source, reference, strain, experiment,
                 bioentity1, bioentity2, modification, annotation_type, bait_hit, note, 
                 date_created, created_by):
        Evidence.__init__(self, bioentity1.display_name + '__' + bioentity2.display_name,
                          bioentity1.format_name + '|' + bioentity2.format_name + '|' + ('-' if strain is None else str(strain.id)) + '|' + bait_hit + '|' + str(experiment.id) + '|' + str(reference.id), 
                          'PHYSINTERACTION', source, reference, strain, experiment,
                          note, date_created, created_by)
        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.modification = modification
        self.annotation_type = annotation_type
        self.bait_hit = bait_hit
        self.note = note

        
        
        