'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String

def create_phenotype_display_name(observable, qualifier, mutant_type):
    if mutant_type is None:
        mutant_type = 'None'
    if qualifier is None:
        display_name = observable + ' in ' + mutant_type + ' mutant'
    else:
        display_name = qualifier + ' ' + observable + ' in ' + mutant_type + ' mutant'
    return display_name

def create_phenotype_format_name(observable, qualifier, mutant_type):
    observable = '.' if observable is None else observable
    qualifier = '.' if qualifier is None else qualifier
    mutant_type = '.' if mutant_type is None else mutant_type
    format_name = qualifier + '|' + observable + '|' + mutant_type
    format_name = format_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

class Phenotype(Bioconcept):
    __tablename__ = "phenotypebioconcept"
    
    id = Column('bioconcept_id', Integer, ForeignKey(Bioconcept.id), primary_key = True)
    observable = Column('observable', String)
    qualifier = Column('qualifier', String)
    mutant_type = Column('mutant_type', String)
    phenotype_type = Column('phenotype_type', String)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, source, sgdid, description,
                 observable, qualifier, mutant_type, phenotype_type, 
                 date_created, created_by):
        Bioconcept.__init__(self, create_phenotype_display_name(observable, qualifier, mutant_type), 
                            create_phenotype_format_name(observable, qualifier, mutant_type), 
                            'PHENOTYPE', None, source, sgdid, description, 
                            date_created, created_by)
        self.observable = observable
        self.qualifier = qualifier
        self.mutant_type = mutant_type
        self.phenotype_type = phenotype_type
        
class Phenotypeevidence(Evidence):
    __tablename__ = "phenotypeevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Phenotype.id))
    
    type = 'BIOCON_EVIDENCE'
    
    #Relationship
    bioentity = relationship(Bioentity, uselist=False)
    bioconcept = relationship(Phenotype, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Evidence.id}
    
    def __init__(self, source, reference, strain, experiment, note,
                 bioentity, phenotype, conditions,
                 date_created, created_by):
        Evidence.__init__(self, 
                          bioentity.display_name + ' ' + phenotype.display_name + ' in ' + reference.display_name,
                          bioentity.format_name + '|' + str(phenotype.id) + ('' if strain is None else ('|' + str(strain.id))) + '|' + str(experiment.id) + '|' + str(reference.id) + '|' + '|'.join(x.format_name for x in conditions), 
                          'PHENOTYPE', source, reference, strain, experiment, note,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.bioconcept_id = phenotype.id
        self.conditions = conditions

    
        
        

    