'''
Created on Oct 25, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, create_format_name
from sqlalchemy.schema import Column, FetchedValue
from sqlalchemy.types import Integer, String, Date

class Bioitem(Base, EqualityByIDMixin):
    __tablename__ = 'bioitem'
    
    id = Column('bioitem_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    __mapper_args__ = {'polymorphic_on': class_type}
    
    def __init__(self, display_name, format_name, class_type, link, source, description):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.description = description 
        
    def unique_key(self):
        return (self.format_name, self.class_type)
        
class Allele(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ALLELE',
                       'inherit_condition': id == Bioitem.id}
    
    def __init__(self, display_name, source, description):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'ALLELE', None, source, description)
        
class Domain(Bioitem):
    __tablename__ = "domainbioitem"
    
    id = Column('bioitem_id', Integer, primary_key=True)
    interpro_id = Column('interpro_id', String)
    interpro_description = Column('interpro_description', String)
    
    __mapper_args__ = {'polymorphic_identity': 'DOMAIN',
                       'inherit_condition': id == Bioitem.id}
    
    def __init__(self, display_name, link, source, description, 
                 interpro_id, interpro_description):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'DOMAIN', link, source, description)
        self.interpro_id = interpro_id
        self.interpro_description = interpro_description
    
class Proteinbioitem(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Bioitem.id}
    
    def __init__(self, display_name, source, description):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'PROTEIN', None, source, description)

class Pathwaybioitem(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'PATHWAY',
                       'inherit_condition': id == Bioitem.id}
    
    def __init__(self, display_name, source, description):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'PROTEIN', None, source, description)

class Dnabioitem(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'DNA',
                       'inherit_condition': id == Bioitem.id}
    
    def __init__(self, display_name, source, description):
        Bioitem.__init__(self, display_name, create_format_name(display_name), 'PROTEIN', None, source, description)