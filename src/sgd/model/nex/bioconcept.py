from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from misc import Url, Alias, Relation
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name


__author__ = 'kpaskov'

class Bioconcept(Base, EqualityByIDMixin):
    __tablename__ = "bioconcept"
        
    id = Column('bioconcept_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    sgdid = Column('sgdid', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"BIOCONCEPT"}
    
    def __init__(self, display_name, format_name, class_type, link, source, sgdid, description, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.sgdid = sgdid
        self.description = description
        self.date_created = date_created
        self.created_by = created_by
        
    def unique_key(self):
        return (self.format_name, self.class_type)

    def to_json(self):
        return {
            'id': self.id,
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            'class_type': self.class_type
            }
      
class Bioconceptrelation(Relation):
    __tablename__ = 'bioconceptrelation'

    id = Column('relation_id', Integer, primary_key=True)
    bioconrel_class_type = Column('subclass', String)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioconcept.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioconcept.id))

    #Relationships
    parent = relationship(Bioconcept, uselist=False, backref=backref("children", passive_deletes=True), primaryjoin="Bioconceptrelation.parent_id==Bioconcept.id")
    child = relationship(Bioconcept, uselist=False, backref=backref("parents", passive_deletes=True), primaryjoin="Bioconceptrelation.child_id==Bioconcept.id")
    
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Relation.id}
   
    def __init__(self, source, relation_type, parent, child, bioconrel_class_type, date_created, created_by):
        Relation.__init__(self, 
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name, 
                          str(parent.id) + '_' + str(child.id) + '_' + bioconrel_class_type, 
                          'BIOCONCEPT', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id
        self.bioconrel_class_type = bioconrel_class_type
    
class Bioconcepturl(Url):
    __tablename__ = 'bioconcepturl'
    
    id = Column('url_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    subclass_type = Column('subclass', String)
        
    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Url.id}
    def __init__(self, display_name, link, source, category, bioconcept, date_created, created_by):
        Url.__init__(self, display_name, bioconcept.format_name, 'BIOCONCEPT', link, source, category,
                     date_created, created_by)
        self.bioconcept_id = bioconcept.id
        self.subclass_type = bioconcept.class_type
    
class Bioconceptalias(Alias):
    __tablename__ = 'bioconceptalias'
    
    id = Column('alias_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    subclass_type = Column('subclass', String)

    bioconcept = relationship(Bioconcept, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, bioconcept, date_created, created_by):
        Alias.__init__(self, display_name, bioconcept.format_name, 'BIOCONCEPT', None, source, category, date_created, created_by)
        self.bioconcept_id = bioconcept.id
        self.subclass_type = bioconcept.class_type

class ECNumber(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "EC_NUMBER",
                       'inherit_condition': id==Bioconcept.id}   
     
    def __init__(self, display_name, source, description, date_created, created_by):
        Bioconcept.__init__(self, display_name + ('' if description is None else ' (' + description + ')'), display_name, 'EC_NUMBER', '/ec_number/' + display_name + '/overview', source, None, description, date_created, created_by)

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['count'] = None if self.count is None else self.count.gene_count
        obj_json['child_count'] = None if self.count is None else self.count.child_gene_count
        obj_json['description'] = self.description
        return obj_json

class Go(Bioconcept):
    __tablename__ = 'gobioconcept'
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_id = Column('go_id', String)
    go_aspect = Column('go_aspect', String)
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}   
     
    def __init__(self, display_name, source, sgdid, description, 
                 go_id, go_aspect, date_created, created_by):
        if display_name == 'biological_process':
            Bioconcept.__init__(self, 'biological process', go_id, 'GO', '/ontology/go/biological_process/overview', source, sgdid, description, date_created, created_by)
        elif display_name == 'molecular_function':
            Bioconcept.__init__(self, 'molecular function', go_id, 'GO', '/ontology/go/molecular_function/overview', source, sgdid, description, date_created, created_by)
        elif display_name == 'cellular_component':
            Bioconcept.__init__(self, 'cellular component', go_id, 'GO', '/ontology/go/cellular_component/overview', source, sgdid, description, date_created, created_by)
        else:
            Bioconcept.__init__(self, display_name, go_id, 'GO', '/go/' + go_id + '/overview', source, sgdid, description, date_created, created_by)
        self.go_id = go_id
        self.go_aspect = go_aspect

    def to_json(self):
        obj_json = Bioconcept.to_json(self)
        obj_json['aspect'] = self.go_aspect
        obj_json['go_id'] = self.go_id
        return obj_json

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['description'] = self.description
        obj_json['aliases'] = [x.to_json() for x in self.aliases]
        obj_json['count'] = self.count.gene_count
        obj_json['child_count'] = self.count.child_gene_count
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
        observable = observable.replace("'", "")
        qualifier = '.' if qualifier is None else qualifier
        format_name = create_format_name(qualifier.lower() + '_' + observable.lower())
    return format_name
        
class Phenotype(Bioconcept):
    __tablename__ = "phenotypebioconcept"
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    phenotype_type = Column('phenotype_type', String)
    is_core_num = Column('is_core', Integer)
    ancestor_type = Column('ancestor_type', String)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, source, sgdid, description,
                 observable, qualifier, phenotype_type, ancestor_type,
                 date_created, created_by):
        if observable == 'observable':
            Bioconcept.__init__(self, 'Yeast Phenotype Ontology', 'ypo', 'PHENOTYPE', '/ontology/phenotype/ypo/overview', source, sgdid, description, date_created, created_by)
        else:
            format_name = create_phenotype_format_name(observable, qualifier)
            link = '/observable/' + format_name + '/overview' if qualifier is None else '/phenotype/' + format_name + '/overview'
            Bioconcept.__init__(self, create_phenotype_display_name(observable, qualifier), format_name, 'PHENOTYPE', link, source, sgdid, description, date_created, created_by)

        self.observable = observable
        self.qualifier = qualifier
        self.phenotype_type = phenotype_type
        self.is_core_num = 1 if self.qualifier is None else 0
        self.ancestor_type = ancestor_type
      
    @hybrid_property  
    def is_core(self):
        return self.is_core_num == 1

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['description'] = self.description
        obj_json['ancestor_type'] = self.ancestor_type
        obj_json['is_core'] = self.is_core
        obj_json['qualifier'] = self.qualifier
        obj_json['observable'] = self.observable
        obj_json['count'] = self.count.gene_count
        obj_json['child_count'] = self.count.child_gene_count
        return obj_json


