from decimal import Decimal
import hashlib

from sqlalchemy import Float, CLOB, Numeric
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric

from bioconcept import Bioconcept, Go, Phenotype, ECNumber
from bioentity import Bioentity, Locus, Complex
from misc import Source, Strain, Experiment, Alias
from bioitem import Bioitem, Domain
from reference import Reference
from bioitem import Contig
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateByJsonMixin

__author__ = 'kpaskov'

class Evidence(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = "evidence"
    
    id = Column('evidence_id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type, 'polymorphic_identity':"EVIDENCE"}

class Property(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'condition'

    id = Column('condition_id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    format_name = Column('format_name', String)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Evidence.id))
    role = Column('role', String)
    note = Column('note', String)

    #Relationships
    evidence = relationship(Evidence, backref=backref('properties', passive_deletes=True), uselist=False)

    __mapper_args__ = {'polymorphic_on': class_type}

    def unique_key(self):
        return self.format_name, self.class_type, self.evidence_id, self.role

class Generalproperty(Property):
    __mapper_args__ = {'polymorphic_identity': 'GENERAL', 'inherit_condition': id == Property.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'role', 'note', 'evidence_id']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = 'g' + hashlib.md5(self.note).hexdigest()[:10]

class Temperatureproperty(Property):
    __tablename__ = 'temperaturecondition'

    id = Column('condition_id', Integer, primary_key=True)
    temperature = Column('temperature', Float)

    __mapper_args__ = {'polymorphic_identity': 'TEMPERATURE', 'inherit_condition': id == Property.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'role', 'note', 'evidence_id',
                     'temperature']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = 't' + str(self.temperature)

class Bioentityproperty(Property):
    __tablename__ = 'bioentitycondition'

    id = Column('condition_id', Integer, primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Property.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'role', 'note', 'evidence_id']
    __eq_fks__ = ['bioentity']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json['bioentity'].id)

class Bioconceptproperty(Property):
    __tablename__ = 'bioconceptcondition'

    id = Column('condition_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    bioconcept = relationship(Bioconcept, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT', 'inherit_condition': id == Property.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'role', 'note', 'evidence_id']
    __eq_fks__ = ['bioconcept']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json['bioconcept'].id)

class Bioitemproperty(Property):
    __tablename__ = 'bioitemcondition'

    id = Column('condition_id', Integer, primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Property.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'role', 'note', 'evidence_id']
    __eq_fks__ = ['bioitem']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json['bioitem'].id)

class Chemicalproperty(Bioitemproperty):
    __tablename__ = 'chemicalcondition'

    id = Column('condition_id', Integer, primary_key=True)
    concentration = Column('amount', String)

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL', 'inherit_condition': id == Property.id}
    __eq_values__ = ['id', 'class_type', 'format_name', 'role', 'note', 'concentration', 'evidence_id']
    __eq_fks__ = ['bioitem']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json['bioitem'].id)

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
    property_key = Column('conditions_key', String)
    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    go_id = Column('bioconcept_id', Integer, ForeignKey(Go.id))

    #Relationships
    source = relationship(Source, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('go_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('go_evidences', passive_deletes=True))
    go = relationship(Go, uselist=False, backref=backref('go_evidences', passive_deletes=True))
    
    __mapper_args__ = {'polymorphic_identity': "GO", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'go_evidence', 'annotation_type', 'qualifier', 'property_key',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus', 'go']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.properties = obj_json['properties']
        self.property_key = None if len(self.properties) == 0 else ';'.join(x.format_name for x in sorted(self.properties, key=lambda x: x.format_name))

    def unique_key(self):
        return self.class_type, self.locus_id, self.go_id, self.go_evidence, self.reference_id, self.property_key

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['properties'] = [x.to_json() for x in self.properties]
        obj_json['go']['go_aspect'] = self.go.go_aspect
        obj_json['go']['go_id'] = self.go.go_id
        if self.go_evidence == 'IEA':
            go_paragraphs = [x for x in self.locus.paragraphs if x.class_type == 'GO']
            if len(go_paragraphs) == 1:
                obj_json['date_created'] = go_paragraphs[0].text
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
    interaction_type = 'Genetic'

    #Relationships
    source = relationship(Source, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('geninteraction_evidences', passive_deletes=True), uselist=False)
    locus1 = relationship(Locus, uselist=False, foreign_keys=[locus1_id], backref=backref('geninteraction_evidences1', passive_deletes=True))
    locus2 = relationship(Locus, uselist=False, foreign_keys=[locus2_id], backref=backref('geninteraction_evidences2', passive_deletes=True))
    phenotype = relationship(Phenotype, uselist=False, backref=backref('geninteraction_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "GENINTERACTION", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'mutant_type', 'annotation_type', 'bait_hit', 'interaction_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus1', 'locus2', 'phenotype']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus1_id, self.locus2_id, self.bait_hit, self.experiment_id, self.reference_id
        
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
    locus1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    locus2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))
    interaction_type = 'Physical'

    #Relationships
    source = relationship(Source, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('physinteraction_evidences', passive_deletes=True), uselist=False)
    locus1 = relationship(Locus, uselist=False, foreign_keys=[locus1_id], backref=backref('physinteraction_evidences1', passive_deletes=True))
    locus2 = relationship(Locus, uselist=False, foreign_keys=[locus2_id], backref=backref('physinteraction_evidences2', passive_deletes=True))
            
    __mapper_args__ = {'polymorphic_identity': "PHYSINTERACTION", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'modification', 'annotation_type', 'bait_hit', 'interaction_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus1', 'locus2']
        
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus1_id, self.locus2_id, self.bait_hit, self.experiment_id, self.reference_id

class Literatureevidence(Evidence):
    __tablename__ = "literatureevidence" 
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    topic = Column('topic', String)
    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    
    #Relationships
    source = relationship(Source, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('literature_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('literature_evidences', passive_deletes=True))
    
    __mapper_args__ = {'polymorphic_identity': "LITERATURE", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'topic',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus_id, self.topic, self.reference_id

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['reference'] = self.reference.to_semi_json()
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
    bioentity = relationship(Bioentity, uselist=False, backref=backref('bioentity_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "BIOENTITY", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'info_key', 'info_value',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'bioentity']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.bioentity_id, self.info_key, self.reference_id, self.strain_id
        
class Phenotypeevidence(Evidence):
    __tablename__ = "phenotypeevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    phenotype_id = Column('bioconcept_id', Integer, ForeignKey(Phenotype.id))
    mutant_type = Column('mutant_type', String)
    strain_details = Column('strain_details', String)
    experiment_details = Column('experiment_details', String)
    property_key = Column('conditions_key', String)
        
    #Relationship
    source = relationship(Source, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('phenotype_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('phenotype_evidences', passive_deletes=True))
    phenotype = relationship(Phenotype, uselist=False, backref=backref('phenotype_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'mutant_type', 'strain_details', 'experiment_details', 'property_key',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus', 'phenotype']
    
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.properties = obj_json['properties']
        self.property_key = None if len(self.properties) == 0 else ';'.join(x.format_name for x in sorted(self.properties, key=lambda x: x.format_name))

    def unique_key(self):
        return self.class_type, self.locus_id, self.phenotype_id, self.strain_id, self.experiment_id, self.reference_id, self.experiment_details, self.mutant_type, self.property_key

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['properties'] = [x.to_json() for x in self.properties]
        obj_json['experiment']['category'] = self.experiment.category
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
    alias = relationship(Alias, uselist=False, backref=backref('alias_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "ALIAS", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'alias']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.alias_id, self.reference_id
        
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
    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    domain_id = Column('bioitem_id', Integer, ForeignKey(Domain.id))
       
    __mapper_args__ = {'polymorphic_identity': 'DOMAIN', 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'start', 'end', 'evalue', 'status', 'date_of_run',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus', 'domain']
    
    #Relationships
    source = relationship(Source, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('domain_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('domain_evidences', passive_deletes=True))
    domain = relationship(Domain, uselist=False, backref=backref('domain_evidences', passive_deletes=True))

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus_id, self.domain_id, self.start, self.end

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['domain']['description'] = self.domain.description
        obj_json['domain']['count'] = self.domain.count
        obj_json['domain']['source'] = self.source.to_min_json()
        return obj_json
        
class Regulationevidence(Evidence):
    __tablename__ = "regulationevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus1_id = Column('bioentity1_id', Integer, ForeignKey(Locus.id))
    locus2_id = Column('bioentity2_id', Integer, ForeignKey(Locus.id))
    property_key = Column('conditions_key', String)
    direction = Column('direction', String)
    fdr = Column('fdr', String)
    pvalue = Column('pvalue', String)
    construct = Column('construct', String)

    #Relationships
    source = relationship(Source, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('regulation_evidences', passive_deletes=True), uselist=False)
    locus1 = relationship(Locus, uselist=False, foreign_keys=[locus1_id], backref=backref('regulation_evidences_targets', passive_deletes=True))
    locus2 = relationship(Locus, uselist=False, foreign_keys=[locus2_id], backref=backref('regulation_evidences_regulators', passive_deletes=True))
       
    __mapper_args__ = {'polymorphic_identity': 'REGULATION', 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'property_key', 'direction', 'fdr', 'pvalue', 'construct',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus1', 'locus2']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.properties = obj_json['properties']
        self.property_key = None if len(self.properties) == 0 else ';'.join(x.format_name for x in sorted(self.properties, key=lambda x: x.format_name))

    def unique_key(self):
        return self.class_type, self.locus1_id, self.locus2_id, self.experiment_id, self.reference_id, self.strain_id, self.property_key

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['properties'] = [x.to_json() for x in self.properties]
        return obj_json

class Expressionevidence(Evidence):
    __tablename__ = "expressionevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    description = Column('description', CLOB)
    geo_id = Column('geo_id', String)
    pcl_filename = Column('pcl_filename', String)
    short_description = Column('short_description', String)
    tags = Column('tags', String)
    condition = Column('condition', String)

    #Relationships
    source = relationship(Source, backref=backref('expression_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('expression_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('expression_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('expression_evidences', passive_deletes=True), uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'EXPRESSION', 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'description', 'geo_id', 'pcl_filename', 'short_description', 'tags', 'condition',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.geo_id, self.condition

class Expressiondata(Base, UpdateByJsonMixin):
    __tablename__ = "expressiondata"

    id = Column('expressiondata_id', Integer, primary_key=True)
    evidence_id = Column('evidence_id', Integer, ForeignKey(Expressionevidence.id))
    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    value = Column('value', Numeric(7, 3))
    class_type = 'EXPRESSION_DATA'

    #Relationships
    evidence = relationship(Expressionevidence, backref=backref('data', passive_deletes=True), uselist=False)
    locus = relationship(Locus, backref=backref('expression_data', passive_deletes=True), uselist=False)

    __eq_values__ = ['id', 'value', 'evidence_id', 'locus_id']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.evidence_id, self.locus_id

    def to_json(self):
        obj_json = self.evidence.to_json()
        obj_json['value'] = float(self.value)
        obj_json['hist_value'] = float(self.value.quantize(Decimal('1.0')))
        obj_json['locus'] = self.locus.to_min_json()
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
    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    total_score = Column('total_score', String)
    expert_confidence = Column('expert_confidence', String)
    motif_id = Column('motif_id', Integer)

    #Relationships
    source = relationship(Source, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('binding_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('binding_evidences', passive_deletes=True))
       
    __mapper_args__ = {'polymorphic_identity': 'BINDING', 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'link', 'total_score', 'expert_confidence', 'motif_id',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.link = "/static/img/yetfasco/" + obj_json['locus'].format_name + "_" + str(self.motif_id) + ".0.png"

    def unique_key(self):
        return self.class_type, self.locus_id, self.motif_id

class Complexevidence(Evidence):
    __tablename__ = "complexevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    complex_id = Column('complex_id', Integer, ForeignKey(Complex.id))
    go_id = Column('go_id', Integer, ForeignKey(Go.id))

    #Relationships
    source = relationship(Source, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('complex_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('complex_evidences', passive_deletes=True))
    complex = relationship(Complex, uselist=False, backref=backref('complex_evidences', passive_deletes=True))
    go = relationship(Go, uselist=False, backref=backref('complex_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'COMPLEX', 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus', 'complex', 'go']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus_id, self.complex_id, self.go_id

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['locus']['description'] = self.locus.description
        return obj_json

class ECNumberevidence(Evidence):
    __tablename__ = "ecnumberevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    ecnumber_id = Column('bioconcept_id', Integer, ForeignKey(ECNumber.id))

    #Relationships
    source = relationship(Source, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('ecnumber_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('ecnumber_evidences', passive_deletes=True))
    ecnumber = relationship(ECNumber, uselist=False, backref=backref('ecnumber_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "ECNUMBER", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus', 'ecnumber']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus_id, self.ecnumber_id

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['locus']['description'] = self.locus.description
        return obj_json

class Proteinexperimentevidence(Evidence):
    __tablename__ = "proteinexperimentevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    data_value = Column('data_value', String)
    data_unit = Column('data_unit', String)

    #Relationships
    source = relationship(Source, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('proteinexperiment_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('proteinexperiment_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "PROTEINEXPERIMENT", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'data_value', 'data_unit',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.class_type, self.locus_id, self.experiment_id

class DNAsequenceevidence(Evidence):
    __tablename__ = "dnasequenceevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
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
    locus = relationship(Locus, uselist=False, backref=backref('dnasequence_evidences', passive_deletes=True))
    contig = relationship(Contig, uselist=False, backref=backref('dnasequence_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "DNASEQUENCE", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'dna_type', 'residues', 'start', 'end', 'strand',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus', 'contig']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['locus']['locus_type'] = self.locus.locus_type
        obj_json['strain']['description'] = self.strain.description
        obj_json['strain']['status'] = self.strain.status
        obj_json['tags'] = [x.to_json() for x in sorted(self.tags, key=lambda x:x.relative_start)]
        return obj_json

    def unique_key(self):
        return self.class_type, self.locus_id, self.strain_id, self.dna_type

class DNAsequencetag(Base, EqualityByIDMixin, UpdateByJsonMixin):
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
    evidence = relationship(DNAsequenceevidence, uselist=False, backref=backref('tags', passive_deletes=True))

    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relative_start', 'relative_end',
                     'chromosomal_start', 'chromosomal_end', 'phase', 'evidence_id',
                     'date_created', 'created_by', ]
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = self.class_type
        self.display_name = self.class_type
        self.class_type = self.class_type.upper()

    def unique_key(self):
        return self.evidence_id, self.class_type, self.chromosomal_start, self.chromosomal_end

class Proteinsequenceevidence(Evidence):
    __tablename__ = "proteinsequenceevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    protein_type = Column('protein_type', String)
    residues = Column('residues', CLOB)

    molecular_weight = Column('molecular_weight', String)
    pi = Column('pi', String)
    cai = Column('cai', String)
    n_term_seq = Column('n_term_seq', String)
    c_term_seq = Column('c_term_seq', String)
    codon_bias = Column('codon_bias', String)
    fop_score = Column('fop_score', String)
    gravy_score = Column('gravy_score', String)
    aromaticity_score = Column('aromaticity_score', String)
    aliphatic_index = Column('aliphatic_index', String)
    instability_index = Column('instability_index', String)

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
    locus = relationship(Locus, uselist=False, backref=backref('proteinsequence_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "PROTEINSEQUENCE", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'protein_type', 'residues', 'molecular_weight', 'pi', 'cai', 'n_term_seq', 'c_term_seq',
                     'codon_bias', 'fop_score', 'gravy_score', 'aromaticity_score', 'aliphatic_index',
                     'instability_index', 'ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly', 'his', 'ile', 'leu',
                     'lys', 'met', 'phe', 'pro', 'thr', 'ser', 'trp', 'tyr', 'val', 'hydrogen', 'sulfur', 'nitrogen',
                     'oxygen', 'carbon', 'yeast_half_life', 'ecoli_half_life', 'mammal_half_life', 'no_cys_ext_coeff',
                     'all_cys_ext_coeff', 'all_half_cys_ext_coeff', 'all_pairs_cys_ext_coeff',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.n_term_seq = self.residues[0:7]
        self.c_term_seq = self.residues[-8:-1]
        self.ala = self.residues.count('A')
        self.arg = self.residues.count('R')
        self.asn = self.residues.count('N')
        self.asp = self.residues.count('D')
        self.cys = self.residues.count('C')
        self.gln = self.residues.count('Q')
        self.glu = self.residues.count('E')
        self.gly = self.residues.count('G')
        self.his = self.residues.count('H')
        self.ile = self.residues.count('I')
        self.leu = self.residues.count('L')
        self.lys = self.residues.count('K')
        self.met = self.residues.count('M')
        self.phe = self.residues.count('F')
        self.pro = self.residues.count('P')
        self.thr = self.residues.count('T')
        self.ser = self.residues.count('S')
        self.trp = self.residues.count('W')
        self.tyr = self.residues.count('Y')
        self.val = self.residues.count('V')

    def unique_key(self):
        return self.class_type, self.locus_id, self.strain_id, self.protein_type

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['strain']['description'] = self.strain.description
        obj_json['strain']['status'] = self.strain.status
        return obj_json

class Phosphorylationevidence(Evidence):
    __tablename__ = "phosphorylationevidence"

    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))
    note = Column('note', String)

    locus_id = Column('bioentity_id', Integer, ForeignKey(Locus.id))
    site_index = Column('site_index', Integer)
    site_residue = Column('site_residue', String)

    #Relationships
    source = relationship(Source, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    reference = relationship(Reference, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    strain = relationship(Strain, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    experiment = relationship(Experiment, backref=backref('phosphorylation_evidences', passive_deletes=True), uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('phosphorylation_evidences', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': "PHOSPHORYLATION", 'inherit_condition': id==Evidence.id}
    __eq_values__ = ['id', 'note',
                     'site_index', 'site_residue',
                     'date_created', 'created_by', ]
    __eq_fks__ = ['source', 'reference', 'strain', 'experiment', 'locus']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.properties = obj_json['properties']

    def unique_key(self):
        return self.class_type, self.locus_id, self.site_residue, self.site_index

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['properties'] = [x.to_json() for x in self.properties]
        return obj_json
