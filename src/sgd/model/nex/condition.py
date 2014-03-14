# -*- coding: utf-8 -*-
import hashlib

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Float

from bioconcept import Bioconcept
from bioentity import Bioentity
from chemical import Chemical
from evidence import Evidence
from bioitem import Bioitem
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base

__author__ = 'kpaskov'

class Condition(Base, EqualityByIDMixin):
    __tablename__ = 'condition'
    
    id = Column('condition_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    class_type = Column('subclass', String)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))
    role = Column('role', String)
    note = Column('note', String)
    
    evidence = relationship(Evidence, backref=backref('conditions', passive_deletes=True), uselist=False)
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    def __init__(self, display_name, format_name, class_type, role, note):
        self.format_name = format_name
        self.display_name = display_name
        self.class_type = class_type
        self.role = role
        self.note = note
        
    def unique_key(self):
        return (self.format_name, self.class_type, self.evidence_id, self.role)
    
class Generalcondition(Condition):
    __mapper_args__ = {'polymorphic_identity': 'CONDITION',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note):
        note = "".join(i for i in note if ord(i)<128)
        Condition.__init__(self, 
                           note,
                           'g' + hashlib.md5(note).hexdigest()[:10],
                           'CONDITION', None, note)
        
class Chemicalcondition(Condition):
    __tablename__ = 'chemicalcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    amount = Column('amount', String) 
    
    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, role, note, chemical, amount):
        Condition.__init__(self, 
                           chemical.display_name if amount is None else amount + ' of ' + chemical.display_name,
                           'c' + str(chemical.id) if amount is None else str(chemical.id) + 'a' + hashlib.md5(amount).hexdigest()[:10],
                           'CHEMICAL', role, note)
        self.chemical_id = chemical.id
        self.amount = amount
        
class Temperaturecondition(Condition):
    __tablename__ = 'temperaturecondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    temperature = Column('temperature', Float)
    
    __mapper_args__ = {'polymorphic_identity': 'TEMPERATURE',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, temperature):
        Condition.__init__(self, str(temperature), 't' + str(temperature),
                           'TEMPERATURE', None, note)
        self.temperature = temperature
        
class Bioentitycondition(Condition):
    __tablename__ = 'bioentitycondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, role, bioentity):
        Condition.__init__(self, role + ' ' + bioentity.display_name,
                           role + str(bioentity.id),
                           'BIOENTITY', role, note)
        self.bioentity_id = bioentity.id
        
class Bioconceptcondition(Condition):
    __tablename__ = 'bioconceptcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, role, bioconcept):
        Condition.__init__(self, role + ' ' + bioconcept.display_name,
                           role + str(bioconcept.id),
                           'BIOCONCEPT', role, note)
        self.bioconcept_id = bioconcept.id
        
class Bioitemcondition(Condition):
    __tablename__ = 'bioitemcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))
    
    __mapper_args__ = {'polymorphic_identity': 'BIOITEM',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, role, bioitem):
        Condition.__init__(self, role + ' ' + bioitem.display_name,
                           role + str(bioitem.id),
                           'BIOITEM', role, note)
        self.bioitem_id = bioitem.id

