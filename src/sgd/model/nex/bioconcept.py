from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from misc import Url, Alias, Relation, Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin


__author__ = 'kpaskov'

class Bioconcept(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = "bioconcept"
        
    id = Column('bioconcept_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    sgdid = Column('sgdid', String)
    description = Column('description', String)
    locus_count = Column('locus_count', Integer)
    descendant_locus_count = Column('descendant_locus_count', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')

    __mapper_args__ = {'polymorphic_on': class_type}
        
    def unique_key(self):
        return self.format_name, self.class_type

class Bioconceptrelation(Relation):
    __tablename__ = 'bioconceptrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioconcept.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    parent = relationship(Bioconcept, uselist=False, backref=backref("children", passive_deletes=True), foreign_keys=[parent_id])
    child = relationship(Bioconcept, uselist=False, backref=backref("parents", passive_deletes=True), foreign_keys=[child_id])
    
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']
   
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        if self.relation_type is not None:
            self.format_name = self.format_name + ' - ' + self.relation_type
            self.display_name = self.display_name + ' - ' + self.relation_type
    
class Bioconcepturl(Url):
    __tablename__ = 'bioconcepturl'
    
    id = Column('url_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    bioconcept = relationship(Bioconcept, uselist=False, backref=backref('urls', passive_deletes=True))
        
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT', 'inherit_condition': id == Url.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioconcept_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioconcept_id'))
    
class Bioconceptalias(Alias):
    __tablename__ = 'bioconceptalias'
    
    id = Column('alias_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    bioconcept = relationship(Bioconcept, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT', 'inherit_condition': id == Alias.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioconcept_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']
    
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioconcept_id'))

class ECNumber(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "EC_NUMBER", 'inherit_condition': id==Bioconcept.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'description',
                     'locus_count', 'descendant_locus_count', 'date_created', 'created_by']
    __eq_fks__ = ['source']
     
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if self.display_name is not None:
            self.link = '/ecnumber/' + self.display_name + '/overview'
        self.format_name = self.display_name

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['urls'] = [x.to_json() for x in sorted(self.urls, key=lambda x: x.display_name)]
        return obj_json

class Go(Bioconcept):
    __tablename__ = 'gobioconcept'
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_id = Column('go_id', String)
    go_aspect = Column('go_aspect', String)
    
    __mapper_args__ = {'polymorphic_identity': "GO", 'inherit_condition': id==Bioconcept.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'description',
                     'locus_count', 'descendant_locus_count', 'go_id', 'go_aspect',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']
     
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if self.display_name == 'biological_process':
            self.display_name = 'biological process'
            self.link = '/ontology/go/biological_process/overview'
            self.format_name = 'biological_process'
        elif self.display_name == 'molecular_function':
            self.display_name = 'molecular function'
            self.link = '/ontology/go/molecular_function/overview'
            self.format_name = 'molecular_function'
        elif self.display_name == 'cellular_component':
            self.display_name = 'cellular component'
            self.link = '/ontology/go/cellular_component/overview'
            self.format_name = 'cellular_component'
        elif self.go_id is not None:
            self.link = '/go/' + self.go_id + '/overview'
            self.format_name = self.go_id

    @hybrid_property
    def evidences(self):
        return self.go_evidences

    @hybrid_property
    def is_root(self):
        return self.format_name == 'biological_process' or self.format_name == 'molecular_function' or self.format_name == 'cellular_component'

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['locus_count'] = self.locus_count
        obj_json['descendant_locus_count'] = self.descendant_locus_count

        obj_json['urls'] = [x.to_json() for x in sorted(self.urls, key=lambda x: x.display_name)]
        obj_json['aliases'] = [x.display_name for x in sorted(self.aliases, key=lambda x: x.display_name)]
        return obj_json
        
def create_phenotype_display_name(observable, qualifier):
    if qualifier is None:
        display_name = observable
    else:
        display_name = observable + ': ' + qualifier
    return display_name

def create_phenotype_format_name(observable, qualifier):
    if qualifier is None:
        format_name = create_format_name(observable.lower())
    else:
        observable = '.' if observable is None else observable
        qualifier = '.' if qualifier is None else qualifier
        format_name = create_format_name(qualifier.lower() + '_' + observable.lower())
    return format_name

class Observable(Bioconcept):
    __tablename__ = "observablebioconcept"

    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key=True)
    ancestor_type = Column('ancestor_type', String)

    __mapper_args__ = {'polymorphic_identity': "OBSERVABLE", 'inherit_condition': id==Bioconcept.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'description',
                     'locus_count', 'descendant_locus_count', 'ancestor_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if self.display_name == 'observable':
            self.display_name = 'Yeast Phenotype Ontology'
            self.format_name = 'ypo'
            self.link = '/ontology/phenotype/ypo/overview'
        else:
            self.format_name = create_format_name(self.display_name.lower())
            self.link = '/observable/' + self.format_name + '/overview'

    @hybrid_property
    def evidences(self):
        return set(sum([x.phenotype_evidences for x in self.phenotypes], []))

    @hybrid_property
    def is_root(self):
        return self.format_name == 'ypo'

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)

        #Phenotype overview
        phenotype_evidences = []
        for phenotype in self.phenotypes:
            phenotype_evidences.extend(phenotype.phenotype_evidences)

        classical_groups = dict()
        large_scale_groups = dict()
        strain_groups = dict()
        for evidence in phenotype_evidences:
            if evidence.experiment.category == 'classical genetics':
                if evidence.mutant_type in classical_groups:
                    classical_groups[evidence.mutant_type] += 1
                else:
                    classical_groups[evidence.mutant_type] = 1
            elif evidence.experiment.category == 'large-scale survey':
                if evidence.mutant_type in large_scale_groups:
                    large_scale_groups[evidence.mutant_type] += 1
                else:
                    large_scale_groups[evidence.mutant_type] = 1

            if evidence.strain is not None:
                if evidence.strain.display_name in strain_groups:
                    strain_groups[evidence.strain.display_name] += 1
                else:
                    strain_groups[evidence.strain.display_name] = 1
        experiment_categories = []
        mutant_types = set(classical_groups.keys())
        mutant_types.update(large_scale_groups.keys())
        for mutant_type in mutant_types:
            experiment_categories.append([mutant_type, 0 if mutant_type not in classical_groups else classical_groups[mutant_type], 0 if mutant_type not in large_scale_groups else large_scale_groups[mutant_type]])

        strains = []
        for strain, count in strain_groups.iteritems():
            strains.append([strain, count])
        experiment_categories.sort(key=lambda x: x[1] + x[2], reverse=True)
        experiment_categories.insert(0, ['Mutant Type', 'classical genetics', 'large-scale survey'])
        strains.sort(key=lambda x: x[1], reverse=True)
        strains.insert(0, ['Strain', 'Annotations'])
        obj_json['overview'] = {'experiment_categories': experiment_categories,
                                          'strains': strains}

        #Phenotypes
        obj_json['phenotypes'] = []
        for phenotype in self.phenotypes:
            phenotype_json = phenotype.to_min_json()
            phenotype_json['qualifier'] = phenotype.qualifier
            obj_json['phenotypes'].append(phenotype_json)

        #Counts
        obj_json['locus_count'] = self.locus_count
        obj_json['descendant_locus_count'] = self.descendant_locus_count

        return obj_json
        
class Phenotype(Bioconcept):
    __tablename__ = "phenotypebioconcept"
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key=True)
    observable_id = Column('observable_id', Integer, ForeignKey(Observable.id))
    qualifier = Column('qualifier', String)

    #Relationships
    observable = relationship(Observable, uselist=False, foreign_keys=[observable_id], lazy='joined', backref=backref('phenotypes', passive_deletes=True))
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE", 'inherit_condition': id==Bioconcept.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'description',
                     'locus_count', 'descendant_locus_count', 'qualifier',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'observable']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = create_phenotype_display_name(obj_json['observable'].display_name, self.qualifier)
        self.format_name = create_phenotype_format_name(obj_json['observable'].display_name, self.qualifier)
        self.link = '/phenotype/' + self.format_name + '/overview'

    @hybrid_property
    def evidences(self):
        return self.phenotype_evidences

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)

        #Phenotype overview
        classical_groups = dict()
        large_scale_groups = dict()
        strain_groups = dict()
        for evidence in self.phenotype_evidences:
            if evidence.experiment.category == 'classical genetics':
                if evidence.mutant_type in classical_groups:
                    classical_groups[evidence.mutant_type] += 1
                else:
                    classical_groups[evidence.mutant_type] = 1
            elif evidence.experiment.category == 'large-scale survey':
                if evidence.mutant_type in large_scale_groups:
                    large_scale_groups[evidence.mutant_type] += 1
                else:
                    large_scale_groups[evidence.mutant_type] = 1
            if evidence.strain is not None:
                if evidence.strain.display_name in strain_groups:
                    strain_groups[evidence.strain.display_name] += 1
                else:
                    strain_groups[evidence.strain.display_name] = 1
        experiment_categories = []
        mutant_types = set(classical_groups.keys())
        mutant_types.update(large_scale_groups.keys())
        for mutant_type in mutant_types:
            experiment_categories.append([mutant_type, 0 if mutant_type not in classical_groups else classical_groups[mutant_type], 0 if mutant_type not in large_scale_groups else large_scale_groups[mutant_type]])

        strains = []
        for strain, count in strain_groups.iteritems():
            strains.append([strain, count])
        experiment_categories.sort(key=lambda x: x[1] + x[2], reverse=True)
        experiment_categories.insert(0, ['Mutant Type', 'classical genetics', 'large-scale survey'])
        strains.sort(key=lambda x: x[1], reverse=True)
        strains.insert(0, ['Strain', 'Annotations'])
        obj_json['overview'] = {'experiment_categories': experiment_categories,
                                          'strains': strains}
        return obj_json


