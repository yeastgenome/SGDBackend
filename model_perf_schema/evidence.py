'''
Created on Oct 28, 2013

@author: kpaskov
'''
from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String
from sqlalchemy.orm import relationship
from core import Bioentity, Bioconcept, Chemical, Reference


class Evidence(Base, EqualityByIDMixin):
        __tablename__ = 'evidence'

        id = Column('evidence_id', Integer, primary_key=True)
        json = Column('json', String)

        def __init__(self, evidence_id, json):
            self.id = evidence_id
            self.json = json

class BioentityEvidence(Base, EqualityByIDMixin):
        __tablename__ = 'bioentity_evidence'

        id = Column('bioentity_evidence_id', Integer, primary_key=True)
        bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
        class_type = Column('class', String)
        evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))

        #Relationships
        evidence = relationship(Evidence, uselist=False)

        def __init__(self, bioentity_id, class_type, evidence_id):
            self.bioentity_id = bioentity_id
            self.class_type = class_type
            self.evidence_id = evidence_id

class BioconceptEvidence(Base, EqualityByIDMixin):
        __tablename__ = 'bioconcept_evidence'

        id = Column('bioconcept_evidence_id', Integer, primary_key=True)
        bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
        class_type = Column('class', String)
        evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))

        #Relationships
        evidence = relationship(Evidence, uselist=False)

        def __init__(self, bioconcept_id, class_type, evidence_id):
            self.bioconcept_id = bioconcept_id
            self.class_type = class_type
            self.evidence_id = evidence_id

class ReferenceEvidence(Base, EqualityByIDMixin):
        __tablename__ = 'reference_evidence'

        id = Column('reference_evidence_id', Integer, primary_key=True)
        reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
        class_type = Column('class', String)
        evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))

        #Relationships
        evidence = relationship(Evidence, uselist=False)

        def __init__(self, reference_id, class_type, evidence_id):
            self.reference_id = reference_id
            self.class_type = class_type
            self.evidence_id = evidence_id

class ChemicalEvidence(Base, EqualityByIDMixin):
        __tablename__ = 'chemical_evidence'

        id = Column('chemical_evidence_id', Integer, primary_key=True)
        bioconcept_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
        class_type = Column('class', String)
        evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))

        #Relationships
        evidence = relationship(Evidence, uselist=False)

        def __init__(self, chemical_id, class_type, evidence_id):
            self.chemical_id = chemical_id
            self.class_type = class_type
            self.evidence_id = evidence_id