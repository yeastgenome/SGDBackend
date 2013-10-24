'''
Created on Dec 11, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.evelement import Experiment, Strain, Source
from model_new_schema.reference import Reference
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    class_type = Column('class', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    source = relationship(Source, backref=backref('evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('evidences', passive_deletes=True), uselist=False)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"EVIDENCE"}
    
    
    def __init__(self, display_name, format_name, class_type, source,
                 reference, strain, experiment, note, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None if strain is None else strain.id
        self.experiment_id = None if experiment is None else experiment.id
        self.note = note
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)

    
        

    
    

        
        

        

          
        