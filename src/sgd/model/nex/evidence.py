import hashlib

from sqlalchemy import Float, CLOB, Numeric
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

from bioconcept import Bioconcept, Go, Phenotype, ECNumber
from bioentity import Bioentity, Protein, Locus, Complex
from misc import Source, Strain, Experiment, Alias
from bioitem import Bioitem, Domain
from reference import Reference
from bioitem import Contig
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateByJsonMixin

__author__ = 'kpaskov'

class Evidence(Base, EqualityByIDMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"EVIDENCE"}

    def __init__(self, class_type, date_created, created_by):
        self.class_type = class_type
        self.date_created = date_created
        self.created_by = created_by

    def to_json(self):
        return {
            'id':self.id,
            'class_type': self.class_type,
            'strain': None if self.strain_id is None else {'id': self.strain_id} if self.strain is None else self.strain.to_min_json(),
            'source': None if self.source_id is None else {'id': self.source_id} if self.source is None else self.source.to_min_json(),
            'reference': None if self.reference_id is None else {'id': self.reference_id} if self.reference is None else self.reference.to_min_json(),
            'experiment': None if self.experiment_id is None else {'id': self.experiment_id} if self.experiment is None else self.experiment.to_min_json(),
            'conditions': [x.to_json() for x in self.conditions],
            'note': self.note}

class Condition(Base, EqualityByIDMixin):
    __tablename__ = 'condition'

    id = Column('condition_id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
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
        obj_json['obj'] = self.bioentity.to_min_json()
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
        obj_json['obj'] = self.bioconcept.to_min_json()
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
        obj_json['obj'] = self.bioitem.to_min_json()
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
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    go_evidence = Column('go_evidence', String)
    annotation_type = Column('annotation_type', String)
    qualifier = Column('qualifier', String)
    conditions_key = Column('conditions_key', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Go.id))

    #Relationships
    source = relationship(Source, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Bioentity, uselist=False, backref='go_evidences')
    bioconcept = relationship(Go, uselist=False, backref='go_evidences')
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, experiment,
                 bioentity, bioconcept,
                 go_evidence, annotation_type, qualifier, conditions,
                 date_created, created_by):
        Evidence.__init__(self, 'GO', date_created, created_by)

        self.source_id = source.id
        self.reference_id = reference.id
        self.strain_id = None
        self.experiment_id = None if experiment is None else experiment.id
        self.note = None

        self.go_evidence = go_evidence
        self.annotation_type = annotation_type
        self.qualifier = qualifier
        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id
        self.conditions = conditions
        self.conditions_key = None if len(conditions) == 0 else ';'.join(x.format_name for x in sorted(conditions, key=lambda x: x.format_name))

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.bioconcept_id, self.go_evidence, self.reference_id, self.conditions_key)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['bioentity'] = self.bioentity.to_json()
        obj_json['go'] = self.bioconcept.to_json()
        obj_json['code'] = self.go_evidence
        obj_json['method'] = self.annotation_type
        obj_json['qualifier'] = self.qualifier
        obj_json['date_created'] = str(self.date_created)
        return obj_json

class Geninteractionevidence(Evidence, UpdateByJsonMixin):
    __tablename__ = "geninteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    phenotype_id = Column('phenotype_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    locus1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    locus2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))

    #Relationships
    source = relationship(Source, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    locus1 = relationship(Locus, uselist=False, foreign_keys=[locus1_id])
    locus2 = relationship(Locus, uselist=False, foreign_keys=[locus2_id])
    phenotype = relationship(Phenotype, uselist=False, backref='geninteraction_evidences')

    __mapper_args__ = {'polymorphic_identity': "GENINTERACTION", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['note', 'mutant_type', 'annotation_type', 'bait_hit']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus1', 'locus2', 'phenotype']

    def __init__(self, source, reference, experiment,
                 locus1, locus2, phenotype, mutant_type, annotation_type, bait_hit, note,
                 date_created, created_by):
        Evidence.__init__(self, 'GENINTERACTION', date_created, created_by)

        self.source_id = None if source is None else source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None
        self.experiment_id = None if experiment is None else experiment.id
        self.note = note

        self.locus1_id = None if locus1 is None else locus1.id
        self.locus2_id = None if locus2 is None else locus2.id
        self.phenotype_id = None if phenotype is None else phenotype.id
        self.mutant_type = mutant_type
        self.annotation_type = annotation_type
        self.bait_hit = bait_hit
        self.note = note

    def unique_key(self):
        return (self.class_type, self.locus1_id, self.locus2_id, self.bait_hit, self.experiment_id, self.reference_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus1'] = {'id': self.locus1_id} if self.locus1 is None else self.locus1.to_json()
        obj_json['locus2'] = {'id': self.locus2_id} if self.locus2 is None else self.locus2.to_json()
        obj_json['phenotype'] = None if self.phenotype_id is None else {'id': self.phenotype_id} if self.phenotype is None else self.phenotype.to_json()
        obj_json['mutant_type'] = self.mutant_type
        obj_json['interaction_type'] = 'Genetic'
        obj_json['annotation_type'] = self.annotation_type
        obj_json['bait_hit'] = self.bait_hit
        return obj_json

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(None, None, None, None, None, None, obj_json.get('mutant_type'), obj_json.get('annotation_type'),
                  obj_json.get('bait_hit'), obj_json.get('note'), None, obj_json.get('date_created'),
                  obj_json.get('created_by'))
        obj.source_id = None if 'source' not in obj_json else obj_json['source']['id']
        obj.reference_id = None if 'reference' not in obj_json else obj_json['reference']['id']
        obj.experiment_id = None if 'experiment' not in obj_json else obj_json['experiment']['id']
        obj.locus1_id = None if 'locus1' not in obj_json else obj_json['locus1']['id']
        obj.locus2_id = None if 'locus2' not in obj_json else obj_json['locus2']['id']
        obj.phenotype_id = None if 'phenotype' not in obj_json else obj_json['phenotype']['id']
        return obj
        
class Physinteractionevidence(Evidence, UpdateByJsonMixin):
    __tablename__ = "physinteractionevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    modification = Column('modification', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String)
    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))

    #Relationships
    source = relationship(Source, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    bioentity1 = relationship(Locus, uselist=False, foreign_keys=[bioentity1_id])
    bioentity2 = relationship(Locus, uselist=False, foreign_keys=[bioentity2_id])
            
    __mapper_args__ = {'polymorphic_identity': "PHYSINTERACTION",
                       'inherit_condition': id==Evidence.id}
    
        
    def __init__(self, source, reference, experiment,
                 bioentity1, bioentity2, modification, annotation_type, bait_hit, note,
                 date_created, created_by):
        Evidence.__init__(self, 'PHYSINTERACTION', date_created, created_by)

        self.source_id = source.id
        self.reference_id = reference.id
        self.strain_id = None
        self.experiment_id = experiment.id
        self.note = note

        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.modification = modification
        self.annotation_type = annotation_type
        self.bait_hit = bait_hit
        self.note = note

    def unique_key(self):
        return (self.class_type, self.bioentity1_id, self.bioentity2_id, self.bait_hit, self.experiment_id, self.reference_id)

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
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    topic = Column('topic', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    
    #Relationships
    source = relationship(Source, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Bioentity, uselist=False, backref='literature_evidences')
    
    __mapper_args__ = {'polymorphic_identity': "LITERATURE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, bioentity, topic, date_created, created_by):
        Evidence.__init__(self, 'LITERATURE', date_created, created_by)
        self.source_id = source.id
        self.reference_id = reference.id
        self.strain_id = None
        self.experiment_id = None
        self.note = None

        self.bioentity_id = None if bioentity is None else bioentity.id
        self.topic = topic

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.topic, self.reference_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['bioentity'] = self.bioentity.to_json()
        obj_json['reference'] = self.reference.to_semi_json()
        obj_json['topic'] = self.topic
        return obj_json

class Bioentityevidence(Evidence):
    __tablename__ = "bioentityevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    info_key = Column('info_key', String)
    info_value = Column('info_value', String)

    #Relationships
    source = relationship(Source, backref=backref('bioentity_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('bioentity_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('bioentity_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('bioentity_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Bioentity, uselist=False, backref='bioentity_evidences')

    __mapper_args__ = {'polymorphic_identity': "BIOENTITY",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, strain, bioentity, info_key, info_value, date_created, created_by):
        Evidence.__init__(self, 'BIOENTITY', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None if strain is None else strain.id
        self.experiment_id = None
        self.note = None

        self.bioentity_id = bioentity.id
        self.info_key = info_key
        self.info_value = info_value

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.info_key, self.reference_id, self.strain_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['bioentity'] = self.bioentity.to_min_json()
        obj_json['reference'] = None if self.reference_id is None else self.reference.to_semi_json()
        obj_json['info_key'] = self.info_key
        obj_json['info_value'] = self.info_value
        return obj_json
        
class Phenotypeevidence(Evidence):
    __tablename__ = "phenotypeevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    strain_details = Column('strain_details', String)
    experiment_details = Column('experiment_details', String)
    conditions_key = Column('conditions_key', String)
        
    #Relationship
    source = relationship(Source, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='phenotype_evidences')
    bioconcept = relationship(Phenotype, uselist=False, backref='phenotype_evidences')

    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Evidence.id}
    
    def __init__(self, source, reference, strain, experiment, note,
                 bioentity, phenotype, mutant_type, strain_details, experiment_details,
                 conditions,
                 date_created, created_by):
        Evidence.__init__(self, 'PHENOTYPE', date_created, created_by)
        self.source_id = source.id
        self.reference_id = reference.id
        self.strain_id = None if strain is None else strain.id
        self.experiment_id = experiment.id
        self.note = note

        self.bioentity_id = bioentity.id
        self.bioconcept_id = phenotype.id
        self.mutant_type = mutant_type
        self.strain_details = strain_details
        self.experiment_details = experiment_details
        self.conditions = conditions
        self.conditions_key = None if len(conditions) == 0 else ';'.join(x.format_name for x in sorted(conditions, key=lambda x: x.format_name))

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.bioconcept_id, self.strain_id, self.experiment_id, self.reference_id, self.experiment_details, self.mutant_type, self.conditions_key)

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

class Aliasevidence(Evidence):
    __tablename__ = "aliasevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    alias_id = Column('alias_id', Integer, ForeignKey(Alias.id))

    #Relationship
    source = relationship(Source, backref=backref('alias_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('alias_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('alias_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('alias_evidences', passive_deletes=True), uselist=False)
    aliases = relationship(Alias, uselist=False, backref='alias_evidences')

    __mapper_args__ = {'polymorphic_identity': "ALIAS",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, alias, date_created, created_by):
        Evidence.__init__(self, 'ALIAS', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None
        self.experiment_id = None
        self.note = None

        self.alias_id = alias.id

    def unique_key(self):
        return (self.class_type, self.alias_id, self.reference_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['alias'] = self.alias.to_json()
        return obj_json
        
class Domainevidence(Evidence):
    __tablename__ = "domainevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    start = Column('start_index', Integer)
    end = Column('end_index', Integer)
    evalue = Column('evalue', String)
    status = Column('domain_status', String)
    date_of_run = Column('date_of_run', Date)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Domain.id))
       
    __mapper_args__ = {'polymorphic_identity': 'DOMAIN',
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    source = relationship(Source, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='domain_evidences')
    bioitem = relationship(Domain, uselist=False, backref="domain_evidences")

    def __init__(self, source, reference, strain, note,
                 start, end, evalue, status, date_of_run, protein, domain,
                 date_created, created_by):
        Evidence.__init__(self, 'DOMAIN', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = strain.id
        self.experiment_id = None
        self.note = note

        self.start = start
        self.end = end
        self.evalue = evalue
        self.status = status
        self.date_of_run = date_of_run
        self.bioentity_id = protein.id
        self.bioitem_id = domain.id

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.bioitem_id, self.start, self.end)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_min_json()
        obj_json['domain'] = self.bioitem.to_min_json()
        obj_json['domain']['count'] = len(set([x.bioentity_id for x in self.bioitem.domain_evidences]))
        obj_json['domain']['description'] = self.bioitem.description
        obj_json['domain']['source'] = self.bioitem.source.to_min_json()
        obj_json['start'] = self.start
        obj_json['end'] = self.end
        obj_json['evalue'] = self.evalue
        obj_json['status'] = self.status
        obj_json['date_of_run'] = self.date_of_run
        return obj_json
        
class Regulationevidence(Evidence):
    __tablename__ = "regulationevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    bioentity2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))
    conditions_key = Column('conditions_key', String)

    #Relationships
    source = relationship(Source, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    bioentity1 = relationship(Locus, uselist=False, foreign_keys=[bioentity1_id])
    bioentity2 = relationship(Locus, uselist=False, foreign_keys=[bioentity2_id])
       
    __mapper_args__ = {'polymorphic_identity': 'REGULATION',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, strain, experiment,
                 bioentity1, bioentity2, conditions,
                 date_created, created_by):
        Evidence.__init__(self, 'REGULATION', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None if strain is None else strain.id
        self.experiment_id = None if experiment is None else experiment.id
        self.note = None

        self.bioentity1_id = bioentity1.id
        self.bioentity2_id = bioentity2.id
        self.conditions = conditions
        self.conditions_key = None if len(conditions) == 0 else ';'.join(x.format_name for x in sorted(conditions, key=lambda x: x.format_name))

    def unique_key(self):
        return (self.class_type, self.bioentity1_id, self.bioentity2_id, self.experiment_id, self.reference_id, self.conditions_key)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus1'] = self.bioentity1.to_json()
        obj_json['locus2'] = self.bioentity2.to_json()
        return obj_json
        
class Bindingevidence(Evidence):
    __tablename__ = "bindingevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    link = Column('obj_url', String)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    total_score = Column('total_score', String)
    expert_confidence = Column('expert_confidence', String)
    motif_id = Column('motif_id', Integer)

    #Relationships
    source = relationship(Source, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='binding_evidences')
       
    __mapper_args__ = {'polymorphic_identity': 'BINDING',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, experiment,
                 bioentity, total_score, expert_confidence, motif_id,
                 date_created, created_by):
        Evidence.__init__(self, 'BINDING', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None
        self.experiment_id = experiment.id
        self.note = None

        self.bioentity_id = bioentity.id
        self.total_score = total_score
        self.expert_confidence = expert_confidence
        self.link = "/static/img/yetfasco/" + bioentity.format_name + "_" + str(motif_id) + ".0.png"
        self.motif_id = motif_id

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.motif_id)

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
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    complex_id = Column('complex_id', Integer, ForeignKey(Complex.id))
    go_id = Column('go_id', Integer, ForeignKey(Go.id))

    #Relationships
    source = relationship(Source, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='complex_evidences')
    complex = relationship(Complex, uselist=False, backref='complex_evidences')
    go = relationship(Go, uselist=False, backref='complex_evidences')

    __mapper_args__ = {'polymorphic_identity': 'COMPLEX',
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, bioentity, complex, go, date_created, created_by):
        Evidence.__init__(self, 'COMPLEX', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None
        self.strain_id = None
        self.experiment_id = None
        self.note = None

        self.bioentity_id = bioentity.id
        self.complex_id = complex.id
        self.go_id = None if go is None else go.id

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.complex_id, self.go_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_json()
        obj_json['complex'] = self.complex.to_json()
        obj_json['go'] = self.go.to_json()
        return obj_json

class ECNumberevidence(Evidence):
    __tablename__ = "ecnumberevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Protein.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(ECNumber.id))

    #Relationships
    source = relationship(Source, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Protein, uselist=False, backref='ecnumber_evidences')
    bioconcept = relationship(ECNumber, uselist=False, backref='ecnumber_evidences')

    __mapper_args__ = {'polymorphic_identity': "ECNUMBER",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, bioentity, bioconcept, date_created, created_by):
        Evidence.__init__(self, 'ECNUMBER', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None
        self.strain_id = None
        self.experiment_id = None
        self.note = None

        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.bioconcept_id)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['protein'] = self.bioentity.to_json()
        obj_json['protein']['locus']['description'] = self.bioentity.description
        obj_json['ecnumber'] = self.bioconcept.to_json()
        return obj_json

class Proteinexperimentevidence(Evidence):
    __tablename__ = "proteinexperimentevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    data_type = Column('data_type', String)
    data_value = Column('data_value', String)

    #Relationships
    source = relationship(Source, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='proteinexperiment_evidences')

    __mapper_args__ = {'polymorphic_identity': "PROTEINEXPERIMENT",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, bioentity, data_type, data_value, date_created, created_by):
        Evidence.__init__(self, 'PROTEINEXPERIMENT', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None
        self.experiment_id = None
        self.note = None

        self.bioentity_id = bioentity.id
        self.data_type = data_type
        self.data_value = data_value

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.data_type)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_min_json()
        obj_json['data_type'] = self.data_type
        obj_json['data_value'] = self.data_value
        return obj_json

class DNAsequenceevidence(Evidence):
    __tablename__ = "dnasequenceevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    dna_type = Column('dna_type', String)
    residues = Column('residues', CLOB)
    contig_id = Column('contig_id', Integer, ForeignKey(Contig.id))
    start = Column('start_index', Integer)
    end = Column('end_index', Integer)
    strand = Column('strand', String)

    #Relationships
    source = relationship(Source, backref=backref('dnasequence_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('dnasequence_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('dnasequence_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('dnasequence_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Bioentity, uselist=False, backref='dnasequence_evidences')
    contig = relationship(Contig, uselist=False, backref='dnasequence_evidences')

    __mapper_args__ = {'polymorphic_identity': "DNASEQUENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, strain, bioentity, dna_type, residues, contig, start, end, strand, date_created, created_by):
        Evidence.__init__(self,"DNASEQUENCE", date_created, created_by)
        self.source_id = source.id
        self.reference_id = None
        self.strain_id = strain.id
        self.experiment_id = None
        self.note = None

        self.bioentity_id = bioentity.id
        self.dna_type = dna_type
        self.residues = residues
        self.contig_id = None if contig is None else contig.id
        self.start = start
        self.end = end
        self.strand = strand

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.strain_id, self.dna_type)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['strain']['description'] = self.strain.description
        obj_json['strain']['is_alternative_reference'] = self.strain.is_alternative_reference
        obj_json['bioentity'] = self.bioentity.to_min_json()
        obj_json['bioentity']['locus_type'] = self.bioentity.locus_type
        obj_json['residues'] = self.residues
        obj_json['contig'] = None if self.contig_id is None else self.contig.to_json()
        obj_json['start'] = self.start
        obj_json['end'] = self.end
        obj_json['strand'] = self.strand
        obj_json['sequence_tags'] = [x.to_json() for x in self.tags]
        obj_json['dna_type'] = self.dna_type
        return obj_json

class DNAsequencetag(Base, EqualityByIDMixin):
    __tablename__ = 'dnasequencetag'

    id = Column('dnasequencetag_id', Integer, primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey(DNAsequenceevidence.id))
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
    evidence = relationship(DNAsequenceevidence, uselist=False, backref='tags')

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

class Proteinsequenceevidence(Evidence):
    __tablename__ = "proteinsequenceevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    protein_type = Column('protein_type', String)
    residues = Column('residues', CLOB)

    molecular_weight = Column('molecular_weight', Numeric)
    pi = Column('pi', Numeric)
    cai = Column('cai', Numeric)
    n_term_seq = Column('n_term_seq', String)
    c_term_seq = Column('c_term_seq', String)
    codon_bias = Column('codon_bias', Numeric)
    fop_score = Column('fop_score', Numeric)
    gravy_score = Column('gravy_score', Numeric)
    aromaticity_score = Column('aromaticity_score', Numeric)
    aliphatic_index = Column('aliphatic_index', Numeric)
    instability_index = Column('instability_index', Numeric)

    ala = Column('ala', Integer)
    arg = Column('arg', Integer)
    asn = Column('asn', Integer)
    asp = Column('asp', Integer)
    cys = Column('cys', Integer)
    gln = Column('gln', Integer)
    glu = Column('glu', Integer)
    gly = Column('gly', Integer)
    his = Column('his', Integer)
    ile = Column('ile', Integer)
    leu = Column('leu', Integer)
    lys = Column('lys', Integer)
    met = Column('met', Integer)
    phe = Column('phe', Integer)
    pro = Column('pro', Integer)
    thr = Column('thr', Integer)
    ser = Column('ser', Integer)
    trp = Column('trp', Integer)
    tyr = Column('tyr', Integer)
    val = Column('val', Integer)

    hydrogen = Column('hydrogen', Integer)
    sulfur = Column('sulfur', Integer)
    nitrogen = Column('nitrogen', Integer)
    oxygen = Column('oxygen', Integer)
    carbon = Column('carbon', Integer)

    yeast_half_life = Column('yeast_half_life', String)
    ecoli_half_life = Column('ecoli_half_life', String)
    mammal_half_life = Column('mammal_half_life', String)

    no_cys_ext_coeff = Column('no_cys_ext_coeff', String)
    all_cys_ext_coeff = Column('all_cys_ext_coeff', String)
    all_half_cys_ext_coeff = Column('all_half_cys_ext_coeff', String)
    all_pairs_cys_ext_coeff = Column('all_pairs_cys_ext_coeff', String)

    #Relationships
    source = relationship(Source, backref=backref('proteinsequence_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('proteinsequence_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('proteinsequence_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('proteinsequence_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='proteinsequence_evidences')

    __mapper_args__ = {'polymorphic_identity': "PROTEINSEQUENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, strain, bioentity, protein_type, residues, date_created, created_by):
        Evidence.__init__(self, "PROTEINSEQUENCE", date_created, created_by)
        self.source_id = source.id
        self.reference_id = None
        self.strain_id = strain.id
        self.experiment_id = None
        self.note = None

        self.bioentity_id = bioentity.id
        self.protein_type = protein_type
        self.residues = residues
        self.n_term_seq = residues[0:7]
        self.c_term_seq = residues[-8:-1]
        self.ala = residues.count('A')
        self.arg = residues.count('R')
        self.asn = residues.count('N')
        self.asp = residues.count('D')
        self.cys = residues.count('C')
        self.gln = residues.count('Q')
        self.glu = residues.count('E')
        self.gly = residues.count('G')
        self.his = residues.count('H')
        self.ile = residues.count('I')
        self.leu = residues.count('L')
        self.lys = residues.count('K')
        self.met = residues.count('M')
        self.phe = residues.count('F')
        self.pro = residues.count('P')
        self.thr = residues.count('T')
        self.ser = residues.count('S')
        self.trp = residues.count('W')
        self.tyr = residues.count('Y')
        self.val = residues.count('V')

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.strain_id, self.protein_type)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['strain']['description'] = self.strain.description
        obj_json['strain']['is_alternative_reference'] = self.strain.is_alternative_reference
        obj_json['bioentity'] = self.bioentity.to_min_json()
        obj_json['residues'] = self.residues
        obj_json['protein_type'] = self.protein_type
        obj_json['pi'] = str(self.pi)
        obj_json['cai'] = str(self.cai)
        obj_json['codon_bias'] = str(self.codon_bias)
        obj_json['fop_score'] = str(self.fop_score)
        obj_json['gravy_score'] = str(self.gravy_score)
        obj_json['aromaticity_score'] = str(self.aromaticity_score)
        obj_json['aliphatic_index'] = str(self.aliphatic_index)
        obj_json['instability_index'] = str(self.instability_index)
        obj_json['molecular_weight'] = None if self.molecular_weight is None else str(round(float(str(self.molecular_weight))))
        obj_json['ala'] = self.ala
        obj_json['arg'] = self.arg
        obj_json['asn'] = self.asn
        obj_json['asp'] = self.asp
        obj_json['cys'] = self.cys
        obj_json['gln'] = self.gln
        obj_json['glu'] = self.glu
        obj_json['gly'] = self.gly
        obj_json['his'] = self.his
        obj_json['ile'] = self.ile
        obj_json['leu'] = self.leu
        obj_json['lys'] = self.lys
        obj_json['met'] = self.met
        obj_json['phe'] = self.phe
        obj_json['pro'] = self.pro
        obj_json['thr'] = self.thr
        obj_json['ser'] = self.ser
        obj_json['trp'] = self.trp
        obj_json['tyr'] = self.tyr
        obj_json['val'] = self.val
        obj_json['hydrogen'] = self.hydrogen
        obj_json['sulfur'] = self.sulfur
        obj_json['oxygen'] = self.oxygen
        obj_json['carbon'] = self.carbon
        obj_json['nitrogen'] = self.nitrogen
        obj_json['yeast_half_life'] = self.yeast_half_life
        obj_json['ecoli_half_life'] = self.ecoli_half_life
        obj_json['mammal_half_life'] = self.mammal_half_life
        obj_json['no_cys_ext_coeff'] = self.no_cys_ext_coeff
        obj_json['all_cys_ext_coeff'] = self.all_cys_ext_coeff
        obj_json['all_half_cys_ext_coeff'] = self.all_half_cys_ext_coeff
        obj_json['all_pairs_cys_ext_coeff'] = self.all_pairs_cys_ext_coeff
        return obj_json

class Phosphorylationevidence(Evidence):
    __tablename__ = "phosphorylationevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    site_index = Column('site_index', Integer)
    site_residue = Column('site_residue', String)

    #Relationships
    source = relationship(Source, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    bioentity = relationship(Locus, uselist=False, backref='phosphorylation_evidences')

    __mapper_args__ = {'polymorphic_identity': "PHOSPHORYLATION",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, source, reference, experiment, bioentity, site_index, site_residue, conditions, date_created, created_by):
        Evidence.__init__(self, 'PHOSPHORYLATION', date_created, created_by)
        self.source_id = source.id
        self.reference_id = None if reference is None else reference.id
        self.strain_id = None
        self.experiment_id = None if experiment is None else experiment.id
        self.conditions = conditions
        self.note = None

        self.bioentity_id = bioentity.id
        self.site_index = site_index
        self.site_residue = site_residue

    def unique_key(self):
        return (self.class_type, self.bioentity_id, self.site_residue, self.site_index)

    def to_json(self):
        obj_json = Evidence.to_json(self)
        obj_json['locus'] = self.bioentity.to_min_json()
        obj_json['site_index'] = self.site_index
        obj_json['site_residue'] = self.site_residue
        return obj_json