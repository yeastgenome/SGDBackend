'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Go(Bioconcept):
    __tablename__ = 'gobioconcept'
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_go_id = Column('go_go_id', Integer)
    go_aspect = Column('go_aspect', String)
    direct_gene_count = Column('direct_gene_count', Integer)
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}   
     
    def __init__(self, bioconcept_id, display_name, format_name, link, description, 
                 go_go_id, go_aspect, date_created, created_by):
        Bioconcept.__init__(self, bioconcept_id, 'GO', display_name, format_name, link,
                            description, date_created, created_by)
        self.go_go_id = go_go_id
        self.go_aspect = go_aspect

class Goevidence(Evidence):
    __tablename__ = "goevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    date_last_reviewed = Column('date_last_reviewed', Date)
    qualifier = Column('qualifier', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Go.id))
    
    #Relationships 
    bioentity = relationship(Bioentity, uselist=False)
    bioconcept = relationship(Go, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, reference_id, source,
                 go_evidence, annotation_type, qualifier, date_last_reviewed,
                bioentity_id, bioconcept_id, date_created, created_by):
        Evidence.__init__(self, evidence_id, 'GO', None, reference_id, None,
                          source, None, date_created, created_by)
        self.go_evidence = go_evidence
        self.annotation_type = annotation_type
        self.qualifier = qualifier
        self.date_last_reviewed = date_last_reviewed
        self.bioentity_id = bioentity_id
        self.bioconcept_id = bioconcept_id
        