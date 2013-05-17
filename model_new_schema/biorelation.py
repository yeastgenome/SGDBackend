'''
Created on Nov 27, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, SCHEMA
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class Biofact(Base, EqualityByIDMixin):
    __tablename__ = 'biofact'

    id = Column('biofact_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    biocon_id = Column('biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    biocon_type = Column('biocon_type', String)
    use_in_graph = Column('use_for_graph', String)

    bioentity = relationship('Bioentity', uselist=False, backref='biofacts')
    bioconcept = relationship('Bioconcept', uselist=False, backref='biofacts')
    
    type = "BIOFACT"

    
    def __init__(self, bioent_id, biocon_id, biocon_type):
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id
        self.biocon_type = biocon_type

class BioentRelation(Base, EqualityByIDMixin):
    __tablename__ = "bioentrel"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
    
    id = Column('biorel_id', Integer, primary_key = True)
    official_name = Column('name', String)
    biorel_type = Column('biorel_type', String)
    source_bioent_id = Column('bioent_id1', Integer, ForeignKey('sprout.bioent.bioent_id'))
    sink_bioent_id = Column('bioent_id2', Integer, ForeignKey('sprout.bioent.bioent_id'))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    type = 'BIORELATION'
    
    #Relationships
    source_bioent = relationship('Bioentity', uselist=False, primaryjoin="BioentRelation.source_bioent_id==Bioentity.id", backref='biorel_source')
    sink_bioent = relationship('Bioentity', uselist=False, primaryjoin="BioentRelation.sink_bioent_id==Bioentity.id", backref='biorel_sink')
        
    __mapper_args__ = {'polymorphic_on': biorel_type,
                       'polymorphic_identity':"BIORELATION",
                       'with_polymorphic':'*'}
    
    @hybrid_property
    def name(self):
        return 'Interaction between ' + self.source_bioent.name + ' and ' + self.sink_bioent.name
        
    def get_opposite(self, bioent):
        if bioent == self.source_bioent:
            return self.sink_bioent
        elif bioent == self.sink_bioent:
            return self.source_bioent
        else:
            return None
        
    @hybrid_property
    def description(self):
        return 'Evidence for interaction between ' + self.source_bioent.full_name + ' and ' + self.sink_bioent.full_name    
        
    @hybrid_property
    def name_with_link(self):
        return 'Interaction between ' + self.source_bioent.name_with_link + ' and ' + self.sink_bioent.name_with_link
    
    def __init__(self, biorel_type, source_bioent_id, sink_bioent_id, session=None, biorel_id=None, created_by=None, date_created=None):
        self.source_bioent_id = source_bioent_id
        self.sink_bioent_id = sink_bioent_id
        self.biorel_type = biorel_type
        
        if session is None:
            self.created_by = created_by
            self.date_created = date_created
            self.id = biorel_id
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.source_bioent.name, self.sink_bioent.name
        return '%s(id=%s, source_name=%s, sink_name=%s)' % data

class BioconRelation(Base, EqualityByIDMixin):
    __tablename__ = 'bioconrel'

    id = Column('biocon_biocon_id', Integer, primary_key=True)
    parent_biocon_id = Column('parent_biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    child_biocon_id = Column('child_biocon_id', Integer, ForeignKey('sprout.biocon.biocon_id'))
    relationship_type = Column('relationship_type', String)
   
    parent_biocon = relationship('Bioconcept', uselist=False, backref='child_biocons', primaryjoin="BioconRelation.parent_biocon_id==Bioconcept.id")
    child_biocon = relationship('Bioconcept', uselist=False, backref='parent_biocons', primaryjoin="BioconRelation.child_biocon_id==Bioconcept.id")
    type = "BIOCON_BIOCON"

    def __init__(self, parent_biocon_id, child_biocon_id, relationship_type, session=None, biocon_biocon_id=None):
        self.parent_biocon_id = parent_biocon_id
        self.child_biocon_id = child_biocon_id
        self.relationship_type = relationship_type
        
        if session is None:
            self.id = biocon_biocon_id
  
class BioconAncestor(Base, EqualityByIDMixin):
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
    
