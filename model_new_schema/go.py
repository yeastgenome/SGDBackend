'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema import SCHEMA
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.biorelation import Biofact
from model_new_schema.evidence import Evidence
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class Go(Bioconcept):
    __tablename__ = 'goterm'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_go_id = Column('go_go_id', Integer)
    go_term = Column('go_term', String)
    go_aspect = Column('go_aspect', String)
    go_definition = Column('go_definition', String)
    direct_gene_count = Column('direct_gene_count', Integer)
    type = "GO"
    
    @hybrid_property
    def search_entry_type(self):
        return 'Gene Ontology Term'

    def __init__(self, biocon_id, go_go_id, go_term, go_aspect, go_definition, date_created, created_by):
        name = go_term.replace(' ', '_')
        name = name.replace('/', '-')
        Bioconcept.__init__(self, biocon_id, 'GO', name, go_definition, date_created, created_by)
        self.go_go_id = go_go_id
        self.go_term = go_term
        self.go_aspect = go_aspect
        self.go_definition = go_definition
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}

class Goevidence(Evidence):
    __tablename__ = "goevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    date_last_reviewed = Column('date_last_reviewed', Date)
    qualifier = Column('qualifier', String)
    
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    biocon_id = Column('biocon_id', Integer, ForeignKey(Go.id))
    
    bioentity = relationship(Bioentity)
    goterm = relationship(Go)
    
    type = 'BIOCON_EVIDENCE'

    __mapper_args__ = {'polymorphic_identity': "GO_EVIDENCE",
                       'inherit_condition': id==Evidence.id}

    
    def __init__(self, evidence_id, biofact_id, reference_id, go_evidence, annotation_type, source, qualifier, date_last_reviewed,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, None, reference_id, 'GO_EVIDENCE', None, date_created, created_by)
        self.biofact_id = biofact_id
        self.go_evidence = go_evidence
        self.annotation_type = annotation_type
        self.source = source
        self.qualifier = qualifier
        self.date_last_reviewed = date_last_reviewed