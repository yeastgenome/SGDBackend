'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, UniqueMixin, subclasses
from model_new_schema.config import SCHEMA
from model_new_schema.mappers import BioentBiocon
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Date
import datetime
    
class Bioconcept(Base, EqualityByIDMixin, UniqueMixin):
    __tablename__ = "biocon"
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}
        
    id = Column('biocon_id', Integer, primary_key = True)
    biocon_type = Column('biocon_type', String)
    name = Column('name', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': biocon_type,
                       'polymorphic_identity':"BIOCONCEPT"}
 
    bioent_biocons = relationship(BioentBiocon, collection_class=attribute_mapped_collection('bioentity'), backref=backref('bioconcept', uselist=False))
    bioentity_evidence = association_proxy('bioent_biocons', 'evidences')
    
    @hybrid_property
    def bioentity(self):
        return self.bioentity_evidence.keys()
    
    @classmethod
    def unique_hash(cls, biocon_type, name):
        return '%s_%s' % (biocon_type, name) 

    @classmethod
    def unique_filter(cls, query, biocon_type, name):
        return query.filter(Bioconcept.biocon_type == biocon_type, Bioconcept.name == name)
        
    def __init__(self, session, source_bioent, sink_bioent):
        self.source_bioent = source_bioent
        self.sink_bioent = sink_bioent
        self.created_by = session.user
        self.date_created = datetime.datetime.now()
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name
        return '%s(id=%s, name=%s)' % data
    
    def __getattr__(self, name):
        if name.endswith('_evidence'):
            name = name[:-9].upper()
            evidence = True
        else:
            name = name.upper()
            evidence = False;

        return self.__get_objects_for_subclass__(name, evidence)

    def __get_objects_for_subclass__(self, subclass_name, evidence=False):
        from model_new_schema.bioentity import Bioentity
        if subclass_name in subclasses(Bioentity):
            if evidence:
                return dict((k, v) for k, v in self.bioentity_evidence.iteritems() if k.bioent_type == subclass_name)
            else:
                return filter(lambda x: x.bioent_type == subclass_name, self.bioentity)
        raise AttributeError()

class Locus(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "LOCUS"}

class Strain(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "STRAIN"}
    
class GOTerm(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "GO_TERM"}

class Phenotype(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE"}
    
class Function(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "FUNCTION"}


    