'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, subclasses, \
    CommonEqualityMixin
from model_new_schema.evidence import Evidence, bioent_biocon_evidence_map
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
  

class Bioconcept(Base, CommonEqualityMixin):
    __tablename__ = "biocon"
    
    id = Column('biocon_id', Integer, primary_key = True)
    type = Column('biocon_type', String)
    name = Column('name', String)
    
    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity':"BIOCONCEPT"}
    
    bioent_biocons = relationship('BioentBiocon', collection_class=attribute_mapped_collection('bioentity'))
    bioentity_evidence = association_proxy('bioent_biocons', 'evidences')
    
    @hybrid_property
    def bioentity(self):
        return self.bioentity_evidence.keys()
        
    def __init__(self, source_bioent, sink_bioent):
        self.source_bioent = source_bioent
        self.sink_bioent = sink_bioent
    
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
        from bioentity_declarative import Bioentity
        if subclass_name in subclasses(Bioentity):
            if evidence:
                return dict((k, v) for k, v in self.bioentity_evidence.iteritems() if k.type == subclass_name)
            else:
                return filter(lambda x: x.type == subclass_name, self.bioentity)
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

class BioentBiocon(Base):
    __tablename__ = 'bioent_biocon'
    __table_args__ = {'extend_existing':True}
    
    bioent_biocon_id = Column('bioent_biocon_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey('bioent.bioent_id'))
    biocon_id = Column('biocon_id', Integer, ForeignKey('biocon.biocon_id'))
    
    bioconcept = relationship('Bioconcept', uselist=False)
    bioentity = relationship('Bioentity', uselist=False)
    evidences = relationship(Evidence, secondary=bioent_biocon_evidence_map)


    