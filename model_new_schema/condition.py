# -*- coding: utf-8 -*-
'''
Created on Oct 21, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, create_format_name
from model_new_schema.bioentity import Bioentity
from model_new_schema.chemical import Chemical
from model_new_schema.evidence import Evidence
from model_new_schema.misc import Allele
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Float
import hashlib

class Condition(Base, EqualityByIDMixin):
    __tablename__ = 'condition'
    
    id = Column('condition_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    class_type = Column('class', String)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))
    note = Column('note', String)
    
    evidence = relationship(Evidence, backref=backref('conditions', passive_deletes=True), uselist=False)
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    def __init__(self, display_name, format_name, class_type, note):
        self.format_name = format_name
        self.display_name = display_name
        self.class_type = class_type
        self.note = note
        
    def unique_key(self):
        return (self.format_name, self.class_type, self.evidence_id)
    
class Generalcondition(Condition):
    __mapper_args__ = {'polymorphic_identity': 'CONDITION',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note):
        note = "".join(i for i in note if ord(i)<128)
        Condition.__init__(self, 
                           note,
                           'g' + hashlib.md5(note).hexdigest()[:10],
                           'CONDITION', note)
        
class Chemicalcondition(Condition):
    __tablename__ = 'chemicalcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    amount = Column('amount', String) 
    
    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, chemical, amount):
        Condition.__init__(self, 
                           chemical.display_name if amount is None else amount + ' of ' + chemical.display_name,
                           'c' + str(chemical.id) if amount is None else str(chemical.id) + 'a' + hashlib.md5(amount).hexdigest()[:10],
                           'CHEMICAL', note)
        self.chemical_id = chemical.id
        self.amount = amount
        
class Background(Base, EqualityByIDMixin):
    __tablename__ = 'background'
    
    id = Column('background_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    description = Column('description', String)
    
    def __init__(self, display_name, source, description):
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.link = None
        self.source = source.id
        self.description = description 
        
class Backgroundcondition(Condition):
    __tablename__ = 'backgroundcondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    background_id = Column('backgroun_id', Integer, ForeignKey(Background.id))
    
    __mapper_args__ = {'polymorphic_identity': 'BACKGROUND',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, background):
        Condition.__init__(self, background.display_name, 'b' + str(background.id),
                           'BACKGROUND', note)
        self.background_id = background.id
        
class Temperaturecondition(Condition):
    __tablename__ = 'temperaturecondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    temperature = Column('temperature', Float)
    
    __mapper_args__ = {'polymorphic_identity': 'TEMPERATURE',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, temperature):
        Condition.__init__(self, str(temperature), 't' + str(temperature),
                           'TEMPERATURE', note)
        self.temperature = temperature
        
class Allelecondition(Condition):
    __tablename__ = 'allelecondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    allele_id = Column('allele_id', Integer, ForeignKey(Allele.id))
    
    __mapper_args__ = {'polymorphic_identity': 'ALLELE',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, allele):
        Condition.__init__(self, allele.display_name, 'a' + str(allele.id),
                           'ALLELE', note)
        self.allele_id = allele.id
        
class Reportercondition(Condition):
    __tablename__ = 'reportercondition'
    
    id = Column('condition_id', Integer, primary_key=True)
    reporter_id = Column('reporter_id', Integer, ForeignKey(Bioentity.id))
    reporter_name = Column('reporter_name', String)
    
    __mapper_args__ = {'polymorphic_identity': 'REPORTER',
                       'inherit_condition': id == Condition.id}
    
    def __init__(self, note, reporter, reporter_name):
        Condition.__init__(self, reporter_name if reporter is None else reporter.display_name,
                           'r' + (reporter_name if reporter is None else str(reporter.id)),
                           'REPORTER', note)
        self.reporter_id = None if reporter is None else reporter.id
