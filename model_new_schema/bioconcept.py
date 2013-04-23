'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin
from model_new_schema.config import SCHEMA
from model_new_schema.link_maker import add_link, link_symbol, biocon_link, \
    bioent_biocon_link
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime


class BioentBiocon(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'bioent_biocon'

    id = Column('bioent_biocon_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.newbioent.bioent_id'))
    biocon_id = Column('biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    biocon_type = Column('biocon_type', String)
    official_name = Column('name', String)
    use_in_graph = Column('use_for_graph', String)    
    
    bioentity = relationship('Bioentity', uselist=False, backref='bioent_biocons')
    bioconcept = relationship('Bioconcept', uselist=False, backref='bioent_biocons')
    type = "BIOENT_BIOCON"

    
    def __init__(self, bioent_id, biocon_id, official_name, biocon_type, session=None):
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id
        self.official_name = official_name
        self.biocon_type = biocon_type
        
    @hybrid_property
    def name(self):
        return self.bioentity.name + link_symbol + self.bioconcept.name
    @hybrid_property
    def link(self):
        return bioent_biocon_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link)

    @hybrid_property
    def description(self):
        return 'Evidence that ' + self.bioentity.name + ' is involved in ' + self.bioconcept.name + '.'  

    @classmethod
    def unique_hash(cls, bioent_id, biocon_id):
        return '%s_%s' % (bioent_id, biocon_id) 
    @classmethod
    def unique_filter(cls, query, bioent_id, biocon_id):
        return query.filter(BioentBiocon.bioent_id == bioent_id, BioentBiocon.biocon_id == biocon_id)

class BioconBiocon(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'biocon_biocon'

    id = Column('biocon_biocon_id', Integer, primary_key=True)
    parent_biocon_id = Column('parent_biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    child_biocon_id = Column('child_biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    relationship_type = Column('relationship_type', String)
   
    parent_biocon = relationship('Bioconcept', uselist=False, backref='child_biocons', primaryjoin="BioconBiocon.parent_biocon_id==Bioconcept.id")
    child_biocon = relationship('Bioconcept', uselist=False, backref='parent_biocons', primaryjoin="BioconBiocon.child_biocon_id==Bioconcept.id")
    type = "BIOCON_BIOCON"

    def __init__(self, parent_biocon_id, child_biocon_id, relationship_type, session=None, biocon_biocon_id=None):
        self.parent_biocon_id = parent_biocon_id
        self.child_biocon_id = child_biocon_id
        self.relationship_type = relationship_type
        
        if session is None:
            self.id = biocon_biocon_id

    @classmethod
    def unique_hash(cls, parent_biocon_id, child_biocon_id, relationship_type):
        return '%s_%s' % (parent_biocon_id, child_biocon_id, relationship_type) 
    @classmethod
    def unique_filter(cls, query, parent_biocon_id, child_biocon_id, relationship_type):
        return query.filter(BioconBiocon.parent_biocon_id == parent_biocon_id, BioconBiocon.child_biocon_id == child_biocon_id, BioconBiocon.relationship_type == relationship_type)  
    
class BioconAncestor(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'biocon_ancestor'

    id = Column('biocon_ancestor_id', Integer, primary_key=True)
    ancestor_biocon_id = Column('ancestor_biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    child_biocon_id = Column('child_biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    generation = Column('generation', Integer)
   
    ancestor_biocon = relationship('Bioconcept', uselist=False, primaryjoin="BioconAncestor.ancestor_biocon_id==Bioconcept.id")
    child_biocon = relationship('Bioconcept', uselist=False, primaryjoin="BioconAncestor.child_biocon_id==Bioconcept.id")
    type = "BIOCON_ANCESTOR"

    def __init__(self, ancestor_biocon_id, child_biocon_id, session=None, biocon_ancestor_id=None):
        self.ancestor_biocon_id = ancestor_biocon_id
        self.child_biocon_id = child_biocon_id
        
        if session is None:
            self.id = biocon_ancestor_id

    @classmethod
    def unique_hash(cls, parent_biocon_id, child_biocon_id):
        return '%s_%s' % (parent_biocon_id, child_biocon_id) 
    @classmethod
    def unique_filter(cls, query, parent_biocon_id, child_biocon_id):
        return query.filter(BioconBiocon.parent_biocon_id == parent_biocon_id, BioconBiocon.child_biocon_id == child_biocon_id)  
    
class Bioconcept(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "biocon"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
    id = Column('biocon_id', Integer, primary_key = True)
    biocon_type = Column('biocon_type', String)
    official_name = Column('name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    type = "BIOCONCEPT"
    description = Column('description', String)
    
    __mapper_args__ = {'polymorphic_on': biocon_type,
                       'polymorphic_identity':"BIOCONCEPT",
                       'with_polymorphic':'*'}
     
    @hybrid_property
    def link(self):
        return biocon_link(self)
    @hybrid_property
    def name(self):
        return self.official_name.title().replace('_', ' ')
    @hybrid_property
    def name_with_link(self):
        return add_link(self.name, self.link)
    
    @classmethod
    def unique_hash(cls, biocon_type, official_name):
        return '%s_%s' % (biocon_type, official_name) 

    @classmethod
    def unique_filter(cls, query, biocon_type, official_name):
        return query.filter(Bioconcept.biocon_type == biocon_type, Bioconcept.official_name == official_name)
        
    def __init__(self, biocon_type, official_name, description, session=None, biocon_id=None, date_created=None, created_by=None):
        self.biocon_type = biocon_type
        self.official_name = official_name
        self.description = description
        
        if session is None:
            self.id=biocon_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.official_name
        return '%s(id=%s, name=%s)' % data
    
class Phenotype(Bioconcept):
    __tablename__ = "phenotype"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
    phenotype_type = Column('phenotype_type', String)
    direct_gene_count = Column('direct_gene_count', Integer)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, observable, phenotype_type, description, session=None, biocon_id=None, date_created=None, created_by=None):
        name = observable.replace(' ', '_')
        name = name.replace('/', '-')
        Bioconcept.__init__(self, 'PHENOTYPE', name, description, session=session, biocon_id=biocon_id, date_created=date_created, created_by=created_by)
        self.observable = str(observable)
        self.phenotype_type = phenotype_type
         
        
    @classmethod
    def unique_hash(cls, qualifier, observable):
        return '%s_%s' % (qualifier, observable) 

    @classmethod
    def unique_filter(cls, query, qualifier, observable):
        return query.filter(Phenotype.qualifier == qualifier, Phenotype.observable == observable)
    
class Go(Bioconcept):
    __tablename__ = 'go_term'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_go_id = Column('go_go_id', Integer)
    go_term = Column('go_term', String)
    go_aspect = Column('go_aspect', String)
    go_definition = Column('go_definition', String)
    direct_gene_count = Column('direct_gene_count', Integer)
    
    def __init__(self, go_go_id, go_term, go_aspect, go_definition, session=None, biocon_id=None, date_created=None, created_by=None):
        name = go_term.replace(' ', '_')
        name = name.replace('/', '-')
        Bioconcept.__init__(self, 'GO', name, go_definition, session=session, biocon_id=biocon_id, date_created=date_created, created_by=created_by)
        self.go_go_id = go_go_id
        self.go_term = go_term
        self.go_aspect = go_aspect
        self.go_definition = go_definition
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}
    
class Function(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "FUNCTION",
                       'inherit_condition': id==Bioconcept.id}
    





    