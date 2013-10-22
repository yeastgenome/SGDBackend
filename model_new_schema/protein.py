'''
Created on Sep 20, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioentity import Protein
from model_new_schema.evidence import Evidence
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
        
def create_domain_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

class Domain(Base, EqualityByIDMixin):
    __tablename__ = "pdomain"
    
    id = Column('pdomain_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    source_id = Column('source_id', String)
    description = Column('description', String)
    interpro_id = Column('interpro_id', String)
    interpro_description = Column('interpro_description', String)
    link = Column('obj_link', String)
    
    def __init__(self, display_name, link, source, description, 
                 interpro_id, interpro_description):
        self.format_name = create_domain_format_name(display_name)
        self.display_name = display_name
        self.link = link
        self.source_id = source.id
        self.description = description
        self.interpro_id = interpro_id
        self.interpro_description = interpro_description
        
    def unique_key(self):
        return self.format_name
    
class Domainevidence(Evidence):
    __tablename__ = "pdomainevidence"
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    start = Column('start_index', Integer)
    end = Column('end_index', Integer)
    evalue = Column('evalue', String)
    status = Column('pdomain_status', String)
    date_of_run = Column('date_of_run', String)
    protein_id = Column('protein_id', Integer, ForeignKey(Protein.id))
    domain_id = Column('pdomain_id', Integer, ForeignKey(Domain.id))
       
    __mapper_args__ = {'polymorphic_identity': 'PDOMAIN',
                       'inherit_condition': id==Evidence.id}
    
    #Relationships
    domain = relationship(Domain, uselist=False)

    def __init__(self, evidence_id, source, reference, strain, note,
                 start, end, evalue, status, date_of_run, protein, domain,
                 date_created, created_by):
        Evidence.__init__(self, evidence_id, protein.format_name + '|' + domain.format_name + '|' + start + '|' + end, 
                          'PDOMAIN', source, reference, strain, None, note, date_created, created_by)
        self.start = start
        self.end = end
        self.evalue = evalue
        self.status = status
        self.date_of_run = date_of_run
        self.protein_id = protein.id
        self.domain_id = domain.id
        
        