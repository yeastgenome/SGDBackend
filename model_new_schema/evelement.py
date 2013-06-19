'''
Created on Jun 10, 2013

@author: kpaskov
'''

from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.link_maker import add_link, experiment_link, strain_link
from model_new_schema.misc import Altid
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Experiment(Base, EqualityByIDMixin):
    __tablename__ = 'experiment'
    
    id = Column('experiment_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String) 
    
    def __init__(self, experiment_id, display_name, format_name, description, date_created, created_by):
        self.id = experiment_id
        self.display_name = display_name
        self.format_name = format_name
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name

    @hybrid_property
    def link(self):
        return experiment_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.link) 
    
    
class ExperimentRelation(Base, EqualityByIDMixin):
    __tablename__ = 'experimentrel'

    id = Column('rel_id', Integer, primary_key = True)
    parent_id = Column('parent_id', Integer, ForeignKey(Experiment.id))
    child_id = Column('child_id', Integer, ForeignKey(Experiment.id))
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    parent_experiment = relationship(Experiment, uselist=False, backref=backref('experimentrels', passive_deletes=True), primaryjoin="ExperimentRelation.parent_id==Experiment.id")
    child_experiment = relationship(Experiment, uselist=False, primaryjoin="ExperimentRelation.child_id==Experiment.id")
    
    def __init__(self, experimentrel_id, parent_id, child_id, date_created, created_by):
        self.id = experimentrel_id
        self.parent_id = parent_id;
        self.child_id = child_id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.parent_id, self.child_id)
        
class ExperimentAltid(Altid):
    __tablename__ = 'experimentaltid'
    
    id = Column('altid_id', Integer, ForeignKey(Altid.id), primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    
    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT_ALTID',
                       'inherit_condition': id == Altid.id}
        
    #Relationships
    reference = relationship(Experiment, uselist=False, backref=backref('altids', passive_deletes=True))
        
    def __init__(self, identifier, source, altid_name, experiment_id, date_created, created_by):
        Altid.__init__(self, identifier, 'EXPERIMENT_ALTID', source, altid_name, date_created, created_by)
        self.experiment_id = experiment_id

class Strain(Base, EqualityByIDMixin):
    __tablename__ = 'strain'

    id = Column('strain_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String) 
    
    def __init__(self, strain_id, display_name, format_name, description, date_created, created_by):
        self.id = strain_id
        self.display_name = display_name;
        self.format_name = format_name
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
    @hybrid_property
    def link(self):
        return strain_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.link) 