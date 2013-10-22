'''
Created on Oct 21, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.chemical import Chemical
from model_new_schema.evidence import Evidence
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Float

class Condition(Base, EqualityByIDMixin):
    __tablename__ = 'condition'
    
    id = Column('condition_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))
    note = Column('note', String)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"CONDITION"}
    
    def __init__(self, class_type, evidence, note):
        self.class_type = class_type
        self.evidence_id = evidence.id
        self.note = note
        
class Chemicalcondition(Condition):
    __tablename__ = 'chemicalcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    amount = Column('amount', String) 
    
    def __init__(self, evidence, note, chemical, amount):
        Condition.__init__(self, 'CHEMICAL', evidence, note)
        self.chemical_id = chemical.id
        self.amount = amount
        
class Background(Base, EqualityByIDMixin):
    __tablename__ = 'background'
    
    id = Column('background_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    
    def __init__(self, display_name, format_name, description):
        self.display_name = display_name
        self.display_name = display_name
        self.description = description 
        
class Backgroundcondition(Condition):
    __tablename__ = 'backgroundcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    background_id = Column('backgroun_id', Integer, ForeignKey(Background.id))
    
    def __init__(self, evidence, note, background):
        Condition.__init__(self, 'BACKGROUND', evidence, note)
        self.background_id = background.id
        
class Temperaturecondition(Condition):
    __tablename__ = 'temperaturecondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    temperature = Column('temperature', Float)
    
    def __init__(self, evidence, note, temperature):
        Condition.__init__(self, 'TEMPERATURE', evidence, note)
        self.temperature = temperature
