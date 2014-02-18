'''
Created on Jun 10, 2013

@author: kpaskov
'''

from model_new_schema import Base, EqualityByIDMixin, create_format_name
from model_new_schema.misc import Alias, Relation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

class Experiment(Base, EqualityByIDMixin):
    __tablename__ = 'experiment'
    
    id = Column('experiment_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    description = Column('description', String)
    eco_id = Column('eco_id', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    def __init__(self, display_name, source, description, eco_id, date_created, created_by):
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.link = None
        self.source_id = source.id
        self.description = description
        self.eco_id = eco_id
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
class Experimentrelation(Relation):
    __tablename__ = 'experimentrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Experiment.id))
    child_id = Column('child_id', Integer, ForeignKey(Experiment.id))
    
    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT',
                       'inherit_condition': id == Relation.id}
    
    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self, parent.format_name + '_' + child.format_name, 
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name, 
                          'EXPERIMENT', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id
    
class Experimentalias(Alias):
    __tablename__ = 'experimentalias'
    
    id = Column('alias_id', Integer, primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))

    experiment = relationship(Experiment, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, experiment, date_created, created_by):
        Alias.__init__(self, display_name, experiment.format_name, 'EXPERIMENT', source, category, date_created, created_by)
        self.experiment_id = experiment.id

class Strain(Base, EqualityByIDMixin):
    __tablename__ = 'strain'

    id = Column('strain_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue()) 
    
    def __init__(self, display_name, source, description, date_created, created_by):
        self.display_name = display_name;
        self.format_name = create_format_name(display_name)
        self.link = None
        self.source_id = source.id
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
class Source(Base, EqualityByIDMixin):
    __tablename__ = 'source'

    id = Column('source_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue()) 
    
    def __init__(self, display_name, description, date_created, created_by):
        self.display_name = display_name;
        self.format_name = create_format_name(display_name)
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    