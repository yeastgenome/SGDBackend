'''
Created on Nov 28, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin, create_format_name
from model_new_schema.misc import Url, Alias, Relation
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

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
      
class Bioconceptrelation(Relation):
    __tablename__ = 'bioconceptrelation'

    id = Column('relation_id', Integer, primary_key=True)
    bioconrel_class_type = Column('subclass', String)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioconcept.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioconcept.id))
    
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
                     bioconcept.id, date_created, created_by)
        self.bioconcept_id = bioconcept.id
        self.subclass_type = bioconcept.class_type
    
class Bioconceptalias(Alias):
    __tablename__ = 'bioconceptalias'
    
    id = Column('alias_id', Integer, primary_key=True)
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id))
    subclass_type = Column('subclass', String)

    __mapper_args__ = {'polymorphic_identity': 'BIOCONCEPT',
                       'inherit_condition': id == Alias.id}
    
    def __init__(self, display_name, source, category, bioconcept, date_created, created_by):
        Alias.__init__(self, display_name, bioconcept.format_name, 'BIOCONCEPT', source, category, date_created, created_by)
        self.bioconcept_id = bioconcept.id
        self.subclass_type = bioconcept.class_type

class ECNumber(Bioconcept):
    __mapper_args__ = {'polymorphic_identity': "EC_NUMBER",
                       'inherit_condition': id==Bioconcept.id}   
     
    def __init__(self, display_name, source, description, date_created, created_by):
        Bioconcept.__init__(self, display_name, display_name, 'EC_NUMBER', 'http://enzyme.expasy.org/EC/' + display_name, source, None, description, date_created, created_by)

class Go(Bioconcept):
    __tablename__ = 'gobioconcept'
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    go_id = Column('go_id', Integer)
    go_aspect = Column('go_aspect', String)
    
    __mapper_args__ = {'polymorphic_identity': "GO",
                       'inherit_condition': id==Bioconcept.id}   
     
    def __init__(self, display_name, source, sgdid, description, 
                 go_id, go_aspect, date_created, created_by):
        Bioconcept.__init__(self, display_name, 'GO:' + str(go_id), 'GO', 
                            'http://www.yeastgenome.org/cgi-bin/GO/goTerm.pl?goid=' + str(go_id), 
                            source, sgdid,
                            description, date_created, created_by)
        self.go_id = go_id
        self.go_aspect = go_aspect
        
def create_phenotype_display_name(observable, qualifier, mutant_type):
    if qualifier is None and mutant_type is None:
        display_name = observable
    else:
        if mutant_type is None:
            mutant_type = 'None'
        if qualifier is None:
            display_name = observable + ' in ' + mutant_type + ' mutant'
        else:
            display_name = qualifier + ' ' + observable + ' in ' + mutant_type + ' mutant'
    return display_name

def create_phenotype_format_name(observable, qualifier, mutant_type):
    if qualifier is None and mutant_type is None:
        format_name = create_format_name(observable)
    else:
        observable = '.' if observable is None else observable
        qualifier = '.' if qualifier is None else qualifier
        mutant_type = '.' if mutant_type is None else mutant_type
        if qualifier is None and mutant_type is None:
            format_name = create_format_name(observable)
        else:  
            format_name = create_format_name(qualifier + '_' + observable + '_' + mutant_type)
    return format_name
        
class Phenotype(Bioconcept):
    __tablename__ = "phenotypebioconcept"
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    mutant_type = Column('mutant_type', String)
    phenotype_type = Column('phenotype_type', String)
    is_core_num = Column('is_core', Integer)
    ancestor_type = Column('ancestor_type', String)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, source, sgdid, description,
                 observable, qualifier, mutant_type, phenotype_type, ancestor_type,
                 date_created, created_by):
        format_name = 'apo_ontology' if observable == 'observable' else create_phenotype_format_name(observable, qualifier, mutant_type)
        display_name = 'APO Ontology' if observable == 'observable' else create_phenotype_display_name(observable, qualifier, mutant_type)
        Bioconcept.__init__(self, display_name, 
                            format_name, 
                            'PHENOTYPE', '/phenotype/' + format_name + '/overview', source, sgdid, description, 
                            date_created, created_by)
        self.observable = observable
        self.qualifier = qualifier
        self.mutant_type = mutant_type
        self.phenotype_type = phenotype_type
        self.is_core_num = 1 if self.mutant_type is None and self.qualifier is None else 0
        self.ancestor_type = ancestor_type
      
    @hybrid_property  
    def is_core(self):
        return self.is_core_num == 1

    