'''
Created on May 15, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity
from model_new_schema.evidence import Evidence
from model_new_schema.misc import Allele
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
    direct_gene_count = Column('direct_gene_count', Integer)
       
    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Bioconcept.id}

    def __init__(self, bioconcept_id, link, source, dbxref, description,
                 observable, qualifier, mutant_type, phenotype_type, 
                 date_created, created_by):
        Bioconcept.__init__(self, bioconcept_id, create_phenotype_display_name(observable, qualifier, mutant_type), 
                            create_phenotype_format_name(observable, qualifier, mutant_type), 
                            'PHENOTYPE', link, source, dbxref, description, 
                            date_created, created_by)
        self.observable = observable
        self.qualifier = qualifier
        self.mutant_type = mutant_type
        self.phenotype_type = phenotype_type
        
class Phenotypeevidence(Evidence):
    __tablename__ = "phenotypeevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    allele_id = Column('allele_id', Integer, ForeignKey(Allele.id))
    
    reporter = Column('reporter', String)
    reporter_desc = Column('reporter_desc', String)
    allele_info = Column('allele_info', String)
    strain_details = Column('strain_details', String)
    details = Column('details', String)
    experiment_details = Column('experiment_details', String)
    conditions = Column('conditions', String)

    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    bioconcept_id = Column('bioconcept_id', Integer, ForeignKey(Phenotype.id))
    
    type = 'BIOCON_EVIDENCE'
    
    #Relationship
    bioentity = relationship(Bioentity, uselist=False)
    bioconcept = relationship(Phenotype, uselist=False)
    allele = relationship(Allele, lazy='subquery', uselist=False, backref='phenotypeevidences')

    __mapper_args__ = {'polymorphic_identity': "PHENOTYPE",
                       'inherit_condition': id==Evidence.id}
    
    def __init__(self, evidence_id, source, reference, strain, experiment, note,
                 bioentity, bioconcept, allele, 
                 allele_info, reporter, reporter_desc, strain_details, experiment_details, conditions, details,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, bioentity.format_name + '|' + bioconcept.format_name + '|' + reference.format_name, 'PHENOTYPE', source, reference, strain, experiment, note,
                          date_created, created_by)
        self.bioentity_id = bioentity.id
        self.bioconcept_id = bioconcept.id
        self.allele_id = allele.id
        
        self.allele_info = allele_info
        self.reporter = reporter
        self.reporter_desc = reporter_desc
        self.strain_details = strain_details
        self.experiment_details = experiment_details
        self.conditions = conditions
        self.details = details

    
        
        

    