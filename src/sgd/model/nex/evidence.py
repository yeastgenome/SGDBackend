import hashlib

from sqlalchemy import Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

from bioconcept import Bioconcept, Go, Phenotype, ECNumber
from bioentity import Bioentity, Protein, Locus, Complex
from misc import Source, Strain, Experiment
from bioitem import Bioitem, Domain
from reference import Reference
from sequence import Sequence, Contig
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base

__author__ = 'kpaskov'

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

    def to_json(self):
        return {
            'id':self.id,
            'class_type': self.class_type,
            'strain': None if self.strain_id is None else self.strain.to_json(),
            'source': None if self.source_id is None else self.source.to_json(),
            'reference': None if self.reference_id is None else self.reference.to_json(),
            'experiment': None if self.experiment_id is None else self.experiment.to_json(),
            'conditions': [x.to_json() for x in self.conditions],
            'note': self.note}

class Condition(Base, EqualityByIDMixin):
    __tablename__ = 'condition'

    id = Column('condition_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    class_type = Column('subclass', String)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))
    role = Column('role', String)
    note = Column('note', String)

    evidence = relationship(Evidence, backref=backref('conditions', passive_deletes=True), uselist=False)

    __mapper_args__ = {'polymorphic_on': class_type}

    def __init__(self, display_name, format_name, class_type, role, note):
        self.format_name = format_name
        self.display_name = display_name
        self.class_type = class_type
        self.role = role
        self.note = note

    def unique_key(self):
        return (self.format_name, self.class_type, self.evidence_id, self.role)

    def to_json(self):
        return {'role': self.role, 'note': self.note, 'class_type': self.class_type}

class Generalcondition(Condition):
    __mapper_args__ = {'polymorphic_identity': 'CONDITION',
                       'inherit_condition': id == Condition.id}

    def __init__(self, note):
        note = "".join(i for i in note if ord(i)<128)
        Condition.__init__(self,
                           note,
                           'g' + hashlib.md5(note).hexdigest()[:10],
                           'CONDITION', None, note)

class Temperaturecondition(Condition):
    __tablename__ = 'temperaturecondition'

    id = Column('condition_id', Integer, primary_key=True)
    temperature = Column('temperature', Float)

    __mapper_args__ = {'polymorphic_identity': 'TEMPERATURE',
                       'inherit_condition': id == Condition.id}

    def __init__(self, note, temperature):
        Condition.__init__(self, str(temperature), 't' + str(temperature),
                           'TEMPERATURE', None, note)
        self.temperature = temperature

    def to_json(self):
        obj_json = Condition.to_json(self)
        obj_json['temperature'] = self.temperature
        return obj_json

class Bioentitycondition(Condition):
    __tablename__ = 'bioentitycondition'

    id = Column('condition_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY',
                       'inherit_condition': id == Condition.id}

    def __init__(self, note, role, bioentity):
        Condition.__init__(self, role + ' ' + bioentity.display_name,
                           role + str(bioentity.id),
                           'BIOENTITY', role, note)
        self.bioentity_id = bioentity.id

    def to_json(self):
        obj_json = Condition.to_json(self)
        obj_json['obj'] = self.bioentity.to_json()
        return obj_json

class Bioconceptcondition(Condition):
    __tablename__ = 'bioconceptcondition'

    id = Column('condition_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    bioconcept = relationship(Bioconcept, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Condition.id}

    def __init__(self, note, role, bioconcept):
        Condition.__init__(self, role + ' ' + bioconcept.display_name,
                           role + str(bioconcept.id),
                           'BIOCONCEPT', role, note)
        self.bioconcept_id = bioconcept.id

    def to_json(self):
        obj_json = Condition.to_json(self)
        obj_json['obj'] = self.bioconcept.to_json()
        return obj_json

class Bioitemcondition(Condition):
    __tablename__ = 'bioitemcondition'

    id = Column('condition_id', Integer, primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM',
                       'inherit_condition': id == Condition.id}

    def __init__(self, note, role, bioitem):
        Condition.__init__(self, role + ' ' + bioitem.display_name,
                           role + str(bioitem.id),
                           'BIOITEM', role, note)
        self.bioitem_id = bioitem.id

    def to_json(self):
        obj_json = Condition.to_json(self)
        obj_json['obj'] = self.bioitem.to_json()
        return obj_json

class Chemicalcondition(Bioitemcondition):
    __tablename__ = 'chemicalcondition'

    id = Column('condition_id', Integer, primary_key=True)
    amount = Column('amount', String)

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL',
                       'inherit_condition': id == Condition.id}

    def __init__(self, role, note, chemical, amount):
        Condition.__init__(self,
                           chemical.display_name if amount is None else amount + ' of ' + chemical.display_name,
                           'c' + str(chemical.id) if amount is None else str(chemical.id) + 'a' + hashlib.md5(amount).hexdigest()[:10],
                           'CHEMICAL', role, note)
        self.bioitem_id = chemical.id
        self.amount = amount

    def to_json(self):
        obj_json = Bioitemcondition.to_json(self)
        obj_json['amount'] = self.amount
        return obj_json

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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['bioentity'] = self.bioentity.to_json()
        obj_json['go'] = self.bioconcept.to_json()
        obj_json['code'] = self.go_evidence
        obj_json['method'] = self.annotation_type
        obj_json['qualifier'] = self.qualifier
        obj_json['date_created'] = str(self.date_created)
        return obj_json

class Geninteractionevidence(Evidence):
    __tablename__ = "geninteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))

    #Relationships
    bioentity1 = relationship(Locus, uselist=False, primaryjoin="Geninteractionevidence.bioentity1_id==Locus.id")
    bioentity2 = relationship(Locus, uselist=False, primaryjoin="Geninteractionevidence.bioentity2_id==Locus.id")
    phenotype = relationship(Phenotype, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "GENINTERACTION",
                       'inherit_condition': id==Evidence.id}

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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus1'] = self.bioentity1.to_json()
        obj_json['locus2'] = self.bioentity2.to_json()
        obj_json['phenotype'] = None if self.phenotype_id is None else self.phenotype.to_json()
        obj_json['mutant_type'] = self.mutant_type
        obj_json['interaction_type'] = 'Genetic'
        obj_json['annotation_type'] = self.annotation_type
        obj_json['bait_hit'] = self.bait_hit
        return obj_json
        
class Physinteractionevidence(Evidence):
    __tablename__ = "physinteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))

    #Relationships
    bioentity1 = relationship(Locus, uselist=False, primaryjoin="Physinteractionevidence.bioentity1_id==Locus.id")
    bioentity2 = relationship(Locus, uselist=False, primaryjoin="Physinteractionevidence.bioentity2_id==Locus.id")
            
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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus1'] = self.bioentity1.to_json()
        obj_json['locus2'] = self.bioentity2.to_json()
        obj_json['modification'] = self.modification
        obj_json['interaction_type'] = 'Physical'
        obj_json['annotation_type'] = self.annotation_type
        obj_json['bait_hit'] = self.bait_hit
        return obj_json

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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['bioentity'] = self.bioentity.to_json()
        obj_json['reference'] = self.reference.to_semi_full_json()
        obj_json['topic'] = self.topic
        return obj_json
        
class Phenotypeevidence(Evidence):
    __tablename__ = "phenotypeevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    strain_details = Column('strain_details', String)
    experiment_details = Column('experiment_details', String)
        
    #Relationship
    bioentity = relationship(Locus, uselist=False)
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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_json()
        obj_json['phenotype'] = self.bioconcept.to_json()
        obj_json['mutant_type'] = self.mutant_type
        obj_json['experiment']['category'] = self.experiment.category

        if obj_json['strain'] is not None:
            obj_json['strain']['details'] = self.strain_details
        if obj_json['experiment'] is not None:
            obj_json['experiment']['details'] = self.experiment_details
        return obj_json
        
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
    bioentity = relationship(Protein, uselist=False)
    bioitem = relationship(Domain, uselist=False, backref="domain_evidences")

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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['protein'] = self.bioentity.to_json()
        obj_json['domain'] = self.bioitem.to_json()
        obj_json['domain']['count'] = len(set([x.bioentity_id for x in self.bioitem.domain_evidences]))
        obj_json['start'] = self.start
        obj_json['end'] = self.end
        obj_json['evalue'] = self.evalue
        obj_json['status'] = self.status
        obj_json['date_of_run'] = self.date_of_run
        return obj_json
          
class Qualifierevidence(Evidence):
    __tablename__ = "qualifierevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    qualifier = Column('qualifier', String)
    
    bioentity = relationship(Locus, uselist=False)
    
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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_json()
        obj_json['qualifier'] = self.qualifier
        return obj_json
        
class Regulationevidence(Evidence):
    __tablename__ = "regulationevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))

    #Relationships
    bioentity1 = relationship(Locus, uselist=False, primaryjoin="Regulationevidence.bioentity1_id==Locus.id")
    bioentity2 = relationship(Locus, uselist=False, primaryjoin="Regulationevidence.bioentity2_id==Locus.id")
       
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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus1'] = self.bioentity1.to_json()
        obj_json['locus2'] = self.bioentity2.to_json()
        return obj_json
        
class Bindingevidence(Evidence):
    __tablename__ = "bindingevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    link = Column('obj_url', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    total_score = Column('total_score', String)
    expert_confidence = Column('expert_confidence', String)
    motif_id = Column('motif_id', Integer)

    #Relationships
    bioentity = relationship(Locus, uselist=False)
       
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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_json()
        obj_json['locus']['description'] = self.bioentity.description
        obj_json['total_score'] = self.total_score
        obj_json['expert_confidence'] = self.expert_confidence
        obj_json['img_url'] = self.link
        obj_json['motif_id'] = self.motif_id
        return obj_json

class Complexevidence(Evidence):
    __tablename__ = "complexevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    complex_id = Column('complex_id', Integer, ForeignKey(Complex.id))
    go_id = Column('go_id', Integer, ForeignKey(Go.id))

    #Relationships
    bioentity = relationship(Locus, uselist=False)
    complex = relationship(Complex, uselist=False)
    go = relationship(Go, uselist=False)

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

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_json()
        obj_json['complex'] = self.complex.to_json()
        obj_json['go'] = self.go.to_json()
        return obj_json

class ECNumberevidence(Evidence):
    __tablename__ = "ecnumberevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Protein.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(ECNumber.id))

    #Relationships
    bioentity = relationship(Protein, uselist=False)
    bioconcept = relationship(ECNumber, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "ECNUMBER",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, bioentity, bioconcept, date_created, created_by):
        Evidence.__init__(self,
                          bioentity.display_name + ' is a ' + bioconcept.display_name,
                          bioentity.format_name + '_' + str(bioconcept.id),
                          'ECNUMBER', source, None, None, None, None,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['protein'] = self.bioentity.to_json()
        obj_json['protein']['locus']['description'] = self.bioentity.description
        obj_json['ecnumber'] = self.bioconcept.to_json()
        return obj_json

class Proteinexperimentevidence(Evidence):
    __tablename__ = "proteinexperimentevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Protein.id))
    data_type = Column('data_type', String)
    data_value = Column('data_value', String)

    #Relationships
    bioentity = relationship(Protein, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "PROTEINEXPERIMENT",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, bioentity, data_type, data_value, date_created, created_by):
        Evidence.__init__(self,
                          bioentity.display_name + ' has ' + data_value + ' ' + data_type,
                          bioentity.format_name,
                          'PROTEINEXPERIMENT', source, reference, None, None, None,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.data_type = data_type
        self.data_value = data_value

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['protein'] = self.bioentity.to_json()
        obj_json['data_type'] = self.data_type
        obj_json['data_value'] = self.data_value
        return obj_json

class Sequenceevidence(Evidence):
    __tablename__ = "sequenceevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    sequence_id = Column('biosequence_id', Integer, ForeignKey(Sequence.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False)
    sequence = relationship(Sequence, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "SEQUENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, strain, class_type, bioentity, sequence, date_created, created_by):
        Evidence.__init__(self,
                          bioentity.display_name + ' has ' + sequence.display_name + ' in strain ' + strain.display_name,
                          bioentity.format_name + '_' + str(sequence.id) + '_' + str(strain.id),
                          class_type, source, None, strain, None, None,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.sequence_id = sequence.id

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['strain']['description'] = self.strain.description
        obj_json['strain']['is_alternative_reference'] = self.strain.is_alternative_reference
        obj_json['bioentity'] = self.bioentity.to_json()
        obj_json['sequence'] = self.sequence.to_json()
        obj_json['sequence_labels'] = [x.to_json() for x in self.labels]
        return obj_json

class SequenceLabel(Base, EqualityByIDMixin):
    __tablename__ = 'sequencelabel'

    id = Column('sequencelabel_id', Integer, primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Sequenceevidence.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    relative_start = Column('relative_start_index', Integer)
    relative_end = Column('relative_end_index', Integer)
    chromosomal_start = Column('chromosomal_start_index', Integer)
    chromosomal_end = Column('chromosomal_end_index', Integer)
    phase = Column('phase', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    evidence = relationship(Sequenceevidence, uselist=False, backref='labels')

    def __init__(self, evidence, class_type, relative_start, relative_end, chromosomal_start, chromosomal_end, phase,
                 date_created, created_by):
        self.evidence_id = evidence.id
        self.display_name = class_type
        self.format_name = class_type
        self.class_type = class_type.upper()
        self.relative_start = relative_start
        self.relative_end = relative_end
        self.chromosomal_start = chromosomal_start
        self.chromosomal_end = chromosomal_end
        self.phase = phase
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.evidence_id, self.class_type, self.chromosomal_start, self.chromosomal_end)

    def to_json(self):
        return {
            'display_name': self.display_name,
            'relative_start': self.relative_start,
            'relative_end': self.relative_end,
            'chromosomal_start': self.chromosomal_start,
            'chromosomal_end': self.chromosomal_end
        }

class GenomicDNAsequenceevidence(Sequenceevidence):
    __tablename__ = "gendnasequenceevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    contig_id = Column('contig_id', Integer, ForeignKey(Contig.id))
    start = Column('start_index', Integer)
    end = Column('end_index', Integer)
    strand = Column('strand', String)

    #Relationships
    contig = relationship(Contig, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "GENDNASEQUENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, strain, bioentity, sequence, contig, start, end, strand, date_created, created_by):
        Sequenceevidence.__init__(self, source, strain, 'GENDNASEQUENCE', bioentity, sequence, date_created, created_by)
        self.contig_id = contig.id
        self.start = start
        self.end = end
        self.strand = strand

    def to_json(self):
        obj_json = Sequenceevidence.to_json(self)
        obj_json['contig'] = None if self.contig_id is None else self.contig.to_json()
        obj_json['start'] = self.start
        obj_json['end'] = self.end
        obj_json['strand'] = self.strand
        return obj_json

class Proteinsequenceevidence(Sequenceevidence):
    __mapper_args__ = {'polymorphic_identity': "PROTEINSEQUENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, strain, bioentity, sequence, date_created, created_by):
        Sequenceevidence.__init__(self, source, strain, 'PROTEINSEQUENCE', bioentity, sequence, date_created, created_by)

class CodingDNAsequenceevidence(Sequenceevidence):
    __mapper_args__ = {'polymorphic_identity': "CODDNASEQUENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, strain, bioentity, sequence, date_created, created_by):
        Sequenceevidence.__init__(self, source, strain, 'CODDNASEQUENCE', bioentity, sequence, date_created, created_by)

class Phosphorylationevidence(Evidence):
    __tablename__ = "phosphorylationevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Protein.id))
    site_index = Column('site_index', Integer)
    site_residue = Column('site_residue', String)

    #Relationships
    bioentity = relationship(Protein, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "PHOSPHORYLATION",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, experiment, bioentity, site_index, site_residue, date_created, created_by):
        Evidence.__init__(self,
                          bioentity.display_name + ' has ' + site_residue + str(site_index),
                          bioentity.format_name + '_' + site_residue + '_' + str(site_index) + ('' if reference is None else '_' + str(reference.id)),
                          'PHOSPHORYLATION', source, reference, None, experiment, None,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.site_index = site_index
        self.site_residue = site_residue

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['protein'] = self.bioentity.to_json()
        obj_json['site_index'] = self.site_index
        obj_json['site_residue'] = self.site_residue
        return obj_json