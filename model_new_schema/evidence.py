'''
Created on Dec 11, 2012

@author: kpaskov
'''
import hashlib
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioconcept import Go, Phenotype
from model_new_schema.bioentity import Bioentity, Protein
from model_new_schema.evelements import Source, Strain, Experiment
from model_new_schema.bioitem import Domain
from model_new_schema.reference import Reference
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    class_type = Column('subclass', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    
    source = relationship(Source, backref=backref('evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('evidences', passive_deletes=True), uselist=False)
    
    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"EVIDENCE"}
    
    
    def __init__(self, display_name, format_name, class_type, source,
                 reference, strain, experiment, note, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None if strain is None else strain.id
        self.experiment_id = None if experiment is None else experiment.id
        self.note = note
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)

class Goevidence(Evidence):
    __tablename__ = "goevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    qualifier = Column('qualifier', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Go.id))
    
    #Relationships 
    bioentity = relationship(Bioentity, uselist=False)
    bioconcept = relationship(Go, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, experiment, note,
                 bioentity, bioconcept, 
                 go_evidence, annotation_type, qualifier, conditions,
                 date_created, created_by):
        Evidence.__init__(self, bioentity.display_name + ' assoc. with ' + bioconcept.display_name + ' with ' + go_evidence + ' by ' + reference.display_name,
                          bioentity.format_name + '_' + str(bioconcept.id) + '_' + go_evidence + '_' + str(reference.id) + ('_'.join(x.format_name for x in conditions)),
                          'GO', source, reference, None, experiment, 
                          note, date_created, created_by)
        self.go_evidence = go_evidence
        self.annotation_type = annotation_type
        self.qualifier = qualifier
        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id
        self.conditions = conditions

class Geninteractionevidence(Evidence):
    __tablename__ = "geninteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
       
    __mapper_args__ = {'polymorphic_identity': "GENINTERACTION",
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    phenotype = relationship(Phenotype)

    def __init__(self, source, reference, strain, experiment,
                 bioentity1, bioentity2, phenotype, mutant_type, annotation_type, bait_hit, note,
                 date_created, created_by):
        Evidence.__init__(self, bioentity1.display_name + '__' + bioentity2.display_name,
                          bioentity1.format_name + '_' + bioentity2.format_name + '_' + ('-' if strain is None else str(strain.id)) + '_' + bait_hit + '_' + str(experiment.id) + '_' + str(reference.id), 
                          'GENINTERACTION', source, reference, strain, experiment, 
                          note, date_created, created_by)
        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.phenotype_id = None if phenotype is None else phenotype.id
        self.mutant_type = mutant_type
        self.annotation_type = annotation_type
        self.bait_hit = bait_hit
        self.note = note
        
class Physinteractionevidence(Evidence):
    __tablename__ = "physinteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
            
    __mapper_args__ = {'polymorphic_identity': "PHYSINTERACTION",
                       'inherit_condition': id==Evidence.id}
    
        
    def __init__(self, source, reference, strain, experiment,
                 bioentity1, bioentity2, modification, annotation_type, bait_hit, note, 
                 date_created, created_by):
        Evidence.__init__(self, bioentity1.display_name + '__' + bioentity2.display_name,
                          bioentity1.format_name + '_' + bioentity2.format_name + '_' + ('-' if strain is None else str(strain.id)) + '_' + bait_hit + '_' + str(experiment.id) + '_' + str(reference.id), 
                          'PHYSINTERACTION', source, reference, strain, experiment,
                          note, date_created, created_by)
        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.modification = modification
        self.annotation_type = annotation_type
        self.bait_hit = bait_hit
        self.note = note

class Literatureevidence(Evidence):
    __tablename__ = "literatureevidence" 
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    topic = Column('topic', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    #Relationships 
    bioentity = relationship(Bioentity, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "LITERATURE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, note,
                            bioentity, topic, date_created, created_by):
        Evidence.__init__(self, 
                          reference.display_name + ' is a ' + topic + ' for ' +  bioentity.display_name,
                          bioentity.format_name + '_' + topic + '_' + reference.format_name, 
                          'LITERATURE', source, reference, None, None, note,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.topic = topic
        
class Phenotypeevidence(Evidence):
    __tablename__ = "phenotypeevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    strain_details = Column('strain_details', String)
    experiment_details = Column('experiment_details', String)
        
    #Relationship
    bioentity = relationship(Bioentity, uselist=False)
    bioconcept = relationship(Phenotype, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Evidence.id}
    
    def __init__(self, source, reference, strain, experiment, note,
                 bioentity, phenotype, mutant_type, strain_details, experiment_details,
                 conditions,
                 date_created, created_by):
        Evidence.__init__(self, 
                          bioentity.display_name + ' ' + phenotype.display_name + ' in ' + reference.display_name,
                          bioentity.format_name + '_' + str(phenotype.id) + '_' + mutant_type + '_' + ('' if strain is None else ('_' + str(strain.id))) + '_' + str(experiment.id) + '_' + str(reference.id) + ('' if experiment_details is None else ('_' + hashlib.md5(experiment_details).hexdigest()[:10])) + '_'.join(x.format_name for x in conditions),
                          'PHENOTYPE', source, reference, strain, experiment, note,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.bioconcept_id = phenotype.id
        self.conditions = conditions
        self.mutant_type = mutant_type
        self.strain_details = strain_details
        self.experiment_details = experiment_details
        
class Domainevidence(Evidence):
    __tablename__ = "domainevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    start = Column('start_index', Integer)
    end = Column('end_index', Integer)
    evalue = Column('evalue', String)
    status = Column('domain_status', String)
    date_of_run = Column('date_of_run', Date)
    bioentity_id = Column('protein_id', Integer, ForeignKey(Protein.id))
    bioitem_id = Column('domain_id', Integer, ForeignKey(Domain.id))
       
    __mapper_args__ = {'polymorphic_identity': 'DOMAIN',
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    domain = relationship(Domain, uselist=False)

    def __init__(self, source, reference, strain, note,
                 start, end, evalue, status, date_of_run, protein, domain,
                 date_created, created_by):
        Evidence.__init__(self, domain.display_name + ' in ' + protein.display_name,
                          protein.format_name + '_' + str(domain.id) + '_' + str(start) + '_' + str(end), 
                          'DOMAIN', source, reference, strain, None, note, date_created, created_by)
        self.start = start
        self.end = end
        self.evalue = evalue
        self.status = status
        self.date_of_run = date_of_run
        self.bioentity_id = protein.id
        self.bioitem_id = domain.id
          
class Qualifierevidence(Evidence):
    __tablename__ = "qualifierevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    qualifier = Column('qualifier', String)
    
    bioentity = relationship(Bioentity, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': 'QUALIFIER',
                       'inherit_condition': id == Evidence.id}
    
    def __init__(self, source, strain, bioentity, qualifier,
                 date_created, created_by):
        Evidence.__init__(self, 
                          bioentity.display_name + ' ' + qualifier + ' in ' + strain.display_name,
                          bioentity.format_name + '_' + strain.format_name, 
                          'QUALIFIER', source, None, strain, None, None, date_created, created_by)
        self.bioentity_id = bioentity.id
        self.qualifier = qualifier
        
class Regulationevidence(Evidence):
    __tablename__ = "regulationevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Bioentity.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Bioentity.id))
       
    __mapper_args__ = {'polymorphic_identity': 'REGULATION',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, strain, experiment, note, 
                 bioentity1, bioentity2, conditions,
                 date_created, created_by):
        Evidence.__init__(self, bioentity1.display_name + '__' + bioentity2.display_name,
                          bioentity1.format_name + '_' + bioentity2.format_name + '_' + ('-' if experiment is None else str(experiment.id)) + '_' + ('-' if reference is None else str(reference.id)) + '_' + ','.join([condition.format_name for condition in conditions]), 
                          'REGULATION', source, reference, strain, experiment, note, date_created, created_by)
        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.conditions = conditions
        
class Bindingevidence(Evidence):
    __tablename__ = "bindingevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    link = Column('obj_url', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    total_score = Column('total_score', String)
    expert_confidence = Column('expert_confidence', String)
    motif_id = Column('motif_id', Integer)
       
    __mapper_args__ = {'polymorphic_identity': 'BINDING',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, strain, experiment, note, 
                 bioentity, total_score, expert_confidence, motif_id,
                 date_created, created_by):
        Evidence.__init__(self, 
                          bioentity.display_name + ' has binding site ' + str(motif_id),
                          bioentity.format_name + '_' + str(motif_id), 
                          'BINDING', source, reference, strain, experiment, note, date_created, created_by)
        self.bioentity_id = bioentity.id
        self.total_score = total_score
        self.expert_confidence = expert_confidence
        self.link = "/static/img/yetfasco/" + bioentity.format_name + "_" + str(motif_id) + ".0.png"
        self.motif_id = motif_id

class Complexevidence(Evidence):
    __tablename__ = "complexevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    complex_id = Column('complex_id', Integer, ForeignKey(Bioentity.id))
    go_id = Column('go_id', Integer, ForeignKey(Bioentity.id))

    __mapper_args__ = {'polymorphic_identity': 'COMPLEX',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, strain, experiment, note,
                 bioentity, complex, go,
                 date_created, created_by):
        Evidence.__init__(self,
                          bioentity.display_name + ' is in complex ' + complex.display_name,
                          bioentity.format_name + '_' + str(complex.id) + ('' if go is None else str(go.id)),
                          'COMPLEX', source, reference, strain, experiment, note, date_created, created_by)
        self.bioentity_id = bioentity.id
        self.complex_id = complex.id
        self.go_id = None if go is None else go.id
