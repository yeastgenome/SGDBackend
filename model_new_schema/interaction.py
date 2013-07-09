'''
Created on May 16, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from model_new_schema.link_maker import add_link, bioent_link_from_basics, \
    bioentrel_link
from model_new_schema.phenotype import Phenotype
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date

class BioentRelation(Base, EqualityByIDMixin):
    __tablename__ = "bioentrel"
    
    id = Column('biorel_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    biorel_type = Column('biorel_type', String)
    source_bioent_id = Column('bioent_id1', Integer, ForeignKey(Bioentity.id))
    sink_bioent_id = Column('bioent_id2', Integer, ForeignKey(Bioentity.id))
    source_format_name = Column('bioent_format_name1', String)
    sink_format_name = Column('bioent_format_name2', String)
    source_display_name = Column('bioent_display_name1', String)
    sink_display_name = Column('bioent_display_name2', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    type = 'BIORELATION'
    
    __mapper_args__ = {'polymorphic_on': biorel_type,
                       'polymorphic_identity':"BIORELATION"}
    
    #Relationships
    #source_bioent = relationship('Bioentity', uselist=False, backref=backref('biorel_source', passive_deletes=True), primaryjoin="BioentRelation.source_bioent_id==Bioentity.id")
    #sink_bioent = relationship('Bioentity', uselist=False, backref=backref('biorel_sink', passive_deletes=True), primaryjoin="BioentRelation.sink_bioent_id==Bioentity.id")
    
    def __init__(self, biorel_id, display_name, format_name, biorel_type, source_bioent_id, sink_bioent_id, source_format_name, sink_format_name, source_display_name, sink_display_name, date_created, created_by):
        self.id = biorel_id
        self.display_name = display_name
        self.format_name = format_name
        self.source_bioent_id = source_bioent_id
        self.sink_bioent_id = sink_bioent_id
        self.source_format_name = source_format_name
        self.sink_format_name = sink_format_name
        self.source_display_name = source_display_name
        self.sink_display_name = sink_display_name
        self.biorel_type = biorel_type
        self.created_by = created_by
        self.date_created = date_created
        
    def unique_key(self):
        return (self.format_name, self.biorel_type)
    
    @hybrid_property
    def endpoint_name_with_links(self):
        return self.source_name_with_link, self.sink_name_with_link
    @hybrid_property
    def source_name_with_link(self):
        return add_link(self.source_display_name, bioent_link_from_basics('LOCUS', self.source_format_name))
    @hybrid_property
    def sink_name_with_link(self):
        return add_link(self.sink_display_name, bioent_link_from_basics('LOCUS', self.sink_format_name))
    @hybrid_property
    def link(self):
        return bioentrel_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(str(self.display_name), self.link)
    @hybrid_property
    def description(self):
        return self.biorel_type.lower() + ' between ' + self.source_bioent.name_with_link + ' and ' + self.sink_bioent.name_with_link


class GeneticInteraction(BioentRelation):
    __tablename__ = "geneticinteraction"

    id = Column('biorel_id', Integer, ForeignKey(BioentRelation.id),primary_key = True)
    evidence_count = Column('evidence_count', Integer)

    __mapper_args__ = {'polymorphic_identity': "GENETIC_INTERACTION",
                       'inherit_condition': id==BioentRelation.id}
    
    def __init__(self, biorel_id, display_name, format_name, 
                                source_bioent_id, sink_bioent_id, 
                                source_format_name, sink_format_name, 
                                source_display_name, sink_display_name, 
                                date_created, created_by):
        BioentRelation.__init__(self, biorel_id, display_name, format_name, 'GENETIC_INTERACTION', 
                                source_bioent_id, sink_bioent_id, 
                                source_format_name, sink_format_name, 
                                source_display_name, sink_display_name, 
                                date_created, created_by)
        self.evidence_count = 0
   
        
class PhysicalInteraction(BioentRelation):
    __tablename__ = "physicalinteraction"

    id = Column('biorel_id', Integer, ForeignKey(BioentRelation.id),primary_key = True)
    evidence_count = Column('evidence_count', Integer)
    
    __mapper_args__ = {'polymorphic_identity': "PHYSICAL_INTERACTION",
                       'inherit_condition': id==BioentRelation.id}
    
    def __init__(self, biorel_id, display_name, format_name, 
                            source_bioent_id, sink_bioent_id, 
                            source_format_name, sink_format_name,
                            source_display_name, sink_display_name,
                            date_created, created_by):
        BioentRelation.__init__(self, biorel_id, display_name, format_name, 'PHYSICAL_INTERACTION', 
                                source_bioent_id, sink_bioent_id, 
                                source_format_name, sink_format_name, 
                                source_display_name, sink_display_name, 
                                date_created, created_by)
        self.evidence_count = 0                    
    
class GeneticInterevidence(Evidence):
    __tablename__ = "geneticinterevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    phenotype_name_with_link = Column('phenotype_name_with_link', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioent1_id = Column('bioent1_id', Integer, ForeignKey(Bioentity.id))
    bioent2_id = Column('bioent2_id', Integer, ForeignKey(Bioentity.id))
    bioent1_name_with_link = Column('bioent1_name_with_link', String)
    bioent2_name_with_link = Column('bioent2_name_with_link', String)
    note = Column('note', String)
    #biorel_id = Column('biorel_id', Integer, ForeignKey(GeneticInteraction.id))
       
    __mapper_args__ = {'polymorphic_identity': "GENETIC_INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    phenotype = relationship(Phenotype)

    def __init__(self, evidence_id, 
                 experiment_id, experiment_name_with_link,
                 reference_id, reference_name_with_link, reference_citation,
                 strain_id, strain_name_with_link,
                 annotation_type, source, 
                 bioent1_id, bioent2_id, bioent1_name_with_link, bioent2_name_with_link,
                 phenotype_id, phenotype_name_with_link, 
                 bait_hit, note, date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_id, experiment_name_with_link,
                          reference_id, reference_name_with_link, reference_citation,
                          strain_id, strain_name_with_link,
                          source, 'GENETIC_INTERACTION_EVIDENCE', date_created, created_by)
        self.annotation_type = annotation_type
        self.phenotype_id = phenotype_id
        self.phenotype_name_with_link = phenotype_name_with_link
        self.bait_hit = bait_hit
        self.note = note
        self.bioent1_id = bioent1_id
        self.bioent2_id = bioent2_id
        self.bioent1_name_with_link = bioent1_name_with_link
        self.bioent2_name_with_link = bioent2_name_with_link
        
class PhysicalInterevidence(Evidence):
    __tablename__ = "physicalinterevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioent1_id = Column('bioent1_id', Integer, ForeignKey(Bioentity.id))
    bioent2_id = Column('bioent2_id', Integer, ForeignKey(Bioentity.id))
    bioent1_name_with_link = Column('bioent1_name_with_link', String)
    bioent2_name_with_link = Column('bioent2_name_with_link', String)
    note = Column('note', String)
            
    __mapper_args__ = {'polymorphic_identity': "PHYSICAL_INTERACTION_EVIDENCE",
                       'inherit_condition': id==Evidence.id}
    
        
    def __init__(self, evidence_id, experiment_id, experiment_name_with_link,
                 reference_id, reference_name_with_link, reference_citation,
                 strain_id, strain_name_with_link,
                 annotation_type, source, 
                 bioent1_id, bioent2_id, bioent1_name_with_link, bioent2_name_with_link,
                 modification, bait_hit, note, date_created, created_by):
        Evidence.__init__(self, evidence_id, experiment_id, experiment_name_with_link,
                          reference_id, reference_name_with_link, reference_citation,
                          strain_id, strain_name_with_link,
                          source, 'PHYSICAL_INTERACTION_EVIDENCE', date_created, created_by)
        self.annotation_type = annotation_type
        self.modification = modification
        self.bait_hit = bait_hit
        self.note = note
        self.bioent1_id = bioent1_id
        self.bioent2_id = bioent2_id
        self.bioent1_name_with_link = bioent1_name_with_link
        self.bioent2_name_with_link = bioent2_name_with_link
        
        
        