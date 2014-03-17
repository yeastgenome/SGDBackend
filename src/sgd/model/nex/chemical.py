from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

from src.sgd.model.nex.misc import Alias, Relation
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name


__author__ = 'kpaskov'

class Chemical(Base, EqualityByIDMixin):
    __tablename__ = "chemical"
    
    id = Column('chemical_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    chebi_id = Column('chebi_id', String)
    description = Column('description', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, display_name, source, chebi_id, description, date_created, created_by):
        self.display_name = display_name
        self.format_name = create_format_name(display_name.lower())[:95]
        self.link = '/chemical/' + self.format_name + '/overview'
        self.source_id = source.id
        self.chebi_id = chebi_id
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return self.format_name
    
    
class Chemicalalias(Alias):
    __tablename__ = 'chemicalalias'
    
    alias_id = Column('alias_id', Integer, primary_key=True)
    chemical_id = Column('bioconcept_id', Integer, ForeignKey(Chemical.id))

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, chemical, date_created, created_by):
        Alias.__init__(self, display_name, chemical.format_name, 'CHEMICAL', None, source, category, date_created, created_by)
        self.chemical_id = chemical.id
        
class Chemicalrelation(Relation):
    __tablename__ = 'chemicalrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Chemical.id))
    child_id = Column('child_id', Integer, ForeignKey(Chemical.id))
    
    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Relation.id}

    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self, 
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name, 
                          str(parent.id) + '_' + str(child.id), 
                          'CHEMICAL', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id
        
        
        