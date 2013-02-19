'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin
from model_new_schema.bioconcept import BioentBiocon
from model_new_schema.biorelation import Biorelation
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import distinct
from sqlalchemy.types import Integer, String, Date, Float
import datetime

class Bioentity(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = 'bioent'
    
    id = Column('bioent_id', Integer, primary_key=True)
    name = Column('name', String)
    bioent_type = Column('bioent_type', String)
    dbxref = Column('dbxref', String)
    source = Column('source', String)
    status = Column('status', String)
    secondary_name = Column('secondary_name', String)
    
    qualifier = Column('qualifier', String)
    attribute = Column('attribute', String)
    short_description = Column('short_description', String)
    headline = Column('headline', String)
    description = Column('description', String)
    genetic_position = Column('genetic_position', String)
    
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': bioent_type,
                       'polymorphic_identity':"BIOENTITY"}

    
    biorel_source = relationship(Biorelation, primaryjoin=Biorelation.sink_bioent_id==id)
    biorel_sink = relationship(Biorelation, primaryjoin=Biorelation.source_bioent_id==id)
    
    bioent_biocons = relationship(BioentBiocon)
    bioconcepts = association_proxy('bioent_biocon', 'bioconcept')
    aliases = relationship("Alias")
    alias_names = association_proxy('aliases', 'name')
        
    def __init__(self, name, bioent_type, dbxref, source, status, secondary_name, 
                 qualifier, attribute, short_description, headline, description, genetic_position,
                 session=None, bioent_id=None, date_created=None, created_by=None):
        self.name = name
        self.bioent_type = bioent_type
        self.dbxref = dbxref
        self.source = source
        self.status = status
        self.secondary_name = secondary_name
        self.qualifier = qualifier
        self.attribute = attribute
        self.short_description = short_description
        self.headline = headline
        self.description = description
        self.genetic_position = genetic_position
        
        if session is None:
            self.id = bioent_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.date_created = datetime.datetime.now()
            self.created_by = session.user
    
    @hybrid_property
    def biorelations(self):
        return set(self.biorel_source + self.biorel_sink)
    
    @classmethod
    def unique_hash(cls, bioent_type, name):
        return '%s_%s' % (bioent_type, name) 

    @classmethod
    def unique_filter(cls, query, bioent_type, name):
        return query.filter(Bioentity.bioent_type == bioent_type, Bioentity.name == name)
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name, self.bioent_type
        return '%s(id=%s, name=%s, bioent_type=%s)' % data       
    
class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    
    id = Column('alias_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('sprout.bioent.bioent_id'))
    name = Column('name', String)
    alias_type = Column('alias_type', String)
    used_for_search = Column('used_for_search', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
        
    def __init__(self, name, alias_type, used_for_search, session=None, alias_id=None, bioent_id=None, date_created=None, created_by=None):
        self.name = name
        self.alias_type = alias_type
        self.used_for_search = used_for_search
        
        if session is None:
            self.id = alias_id
            self.bioent_id = bioent_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.date_created = datetime.datetime.now()
            self.created_by = session.user             
                       
class Gene(Bioentity):
    __tablename__ = "gene"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    gene_name = Column('gene_name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_identity': 'ORF',
                       'inherit_condition': id == Bioentity.id}

    def __init__(self, name, bioent_type, taxon_id, dbxref, source, gene_name):
        super(Bioentity, self).__init__(name, bioent_type, taxon_id, dbxref, source)
        self.gene_name = gene_name
        
class Protein(Bioentity):
    __tablename__ = "protein"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    molecular_weight = Column('molecular_weight', Integer)
    pi = Column('pi', Float)
    cai = Column('cai', Float)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    #gene_id = Column('gene_id', Integer, ForeignKey('gene.bioent_id'))
    
    #Relationships
    #gene = relationship('Gene', backref='proteins')
    
    __mapper_args__ = {'polymorphic_identity': "PROTEIN",
                       'inherit_condition': id == Bioentity.id}

    def __init__(self, name, bioent_type, taxon_id, dbxref, source):
        super(Bioentity, self).__init__(name, bioent_type, taxon_id, dbxref, source)
        
#Gene Subclasses
gene_subclass_names = {'TRNA', 'SNORNA', 'RRNA', 'NCRNA', 'SNRNA'}

for gene_subclass_name in gene_subclass_names:
    class_name = gene_subclass_name
    globals()[class_name] = type(class_name, (Gene,), {'__mapper_args__':{'polymorphic_identity': gene_subclass_name, 'inherit_condition': id == Bioentity.id}}).__class__

def create_bioentity_subclasses(session=None):
    #All other subclasses of Bioentity.
    def f(session):
        result = session.query(distinct(Bioentity.bioent_type))
        for row in result:
            try:
                bioent_type = str(row[0])
                globals()[bioent_type.upper()]
            except:
                type(bioent_type.capitalize(), (Bioentity,), {'__mapper_args__':{'polymorphic_identity': bioent_type, 'inherit_condition': id == Bioentity.id}})
    return f if session is None else f(session)


