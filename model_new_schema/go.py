'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
from model_new_schema import Base, EqualityByIDMixin

class Go(Bioconcept):
    __tablename__ = 'goterm'
    
    id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_go_id = Column('go_go_id', Integer)
    go_aspect = Column('go_aspect', String)
    direct_gene_count = Column('direct_gene_count', Integer)
    type = "GO"
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}   
     
    def __init__(self, biocon_id, display_name, format_name, description, 
                 go_go_id, go_aspect, date_created, created_by):
        Bioconcept.__init__(self, biocon_id, 'GO', display_name, format_name, 
                            description, date_created, created_by)
        self.go_go_id = go_go_id
        self.go_aspect = go_aspect
        
    @hybrid_property
    def search_entry_type(self):
        return 'Gene Ontology Term'
    @hybrid_property
    def subtype(self):
        return self.go_aspect
    @hybrid_property
    def weight(self):
        return self.direct_gene_count

class Goevidence(Evidence):
    __tablename__ = "goevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    date_last_reviewed = Column('date_last_reviewed', Date)
    qualifier = Column('qualifier', String)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    biocon_id = Column('biocon_id', Integer, ForeignKey(Go.id))
    type = 'BIOCON_EVIDENCE'  
    
    #Relationships 
    bioentity = relationship(Bioentity, uselist=False)
    bioconcept = relationship(Go, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "GO_EVIDENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, reference_id, reference_name_with_link, reference_citation, source,
                 go_evidence, annotation_type, qualifier, date_last_reviewed,
                bioent_id, biocon_id, date_created, created_by):
        Evidence.__init__(self, evidence_id, None, None,
                          reference_id, reference_name_with_link, reference_citation,
                          None, None,
                          source, 'GO_EVIDENCE', date_created, created_by)
        self.go_evidence = go_evidence
        self.annotation_type = annotation_type
        self.qualifier = qualifier
        self.date_last_reviewed = date_last_reviewed
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id
        
class Gofact(Base, EqualityByIDMixin):
    __tablename__ = 'gofact'

    id = Column('biofact_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    biocon_id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id))
    type = "BIOFACT"

    
    def __init__(self, bioent_id, biocon_id):
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id

    def unique_key(self):
        return (self.bioent_id, self.biocon_id)
        
        