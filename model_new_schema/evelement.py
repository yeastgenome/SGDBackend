'''
Created on Jun 10, 2013

@author: kpaskov
'''

from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.misc import Alias
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Experiment(Base, EqualityByIDMixin):
    __tablename__ = 'experiment'
    
    id = Column('experiment_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_link', String)
    description = Column('description', String)
    eco_id = Column('eco_id', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String) 
    
    def __init__(self, experiment_id, display_name, format_name, link, description, eco_id, date_created, created_by):
        self.id = experiment_id
        self.display_name = display_name
        self.format_name = format_name
        self.link = link
        self.description = description
        self.eco_id = eco_id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
    
class ExperimentRelation(Base, EqualityByIDMixin):
    __tablename__ = 'experiment_relation'

    id = Column('experiment_relation_id', Integer, primary_key = True)
    parent_experiment_id = Column('parent_experiment_id', Integer, ForeignKey(Experiment.id))
    child_experiment_id = Column('child_experiment_id', Integer, ForeignKey(Experiment.id))
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    #Relationships
    parent_experiment = relationship(Experiment, uselist=False, backref=backref('child_experiment_relations', passive_deletes=True), primaryjoin="ExperimentRelation.parent_experiment_id==Experiment.id")
    child_experiment = relationship(Experiment, uselist=False, primaryjoin="ExperimentRelation.child_experiment_id==Experiment.id")
    
    def __init__(self, experimentrel_id, parent_experiment_id, child_experiment_id, date_created, created_by):
        self.id = experimentrel_id
        self.parent_experiment_id = parent_experiment_id;
        self.child_experiment_id = child_experiment_id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.parent_experiment_id, self.child_experiment_id)
        
class Experimentalias(Alias):
    __tablename__ = 'experimentalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    
    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT',
                       'inherit_condition': id == Alias.id}
        
    #Relationships
    reference = relationship(Experiment, uselist=False, backref=backref('aliases', passive_deletes=True))
        
    def __init__(self, display_name, source, category, experiment_id, date_created, created_by):
        Alias.__init__(self, 'EXPERIMENT', display_name, source, category, date_created, created_by)
        self.experiment_id = experiment_id
        
    def unique_key(self):
        return (self.display_name, self.experiment_id)

class Strain(Base, EqualityByIDMixin):
    __tablename__ = 'strain'

    id = Column('strain_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_link', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String) 
    
    def __init__(self, strain_id, display_name, format_name, link, description, date_created, created_by):
        self.id = strain_id
        self.display_name = display_name;
        self.format_name = format_name
        self.link = link
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    