'''
Created on Nov 27, 2012

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity import Bioentity

class Biofact(Base, EqualityByIDMixin):
    __tablename__ = 'biofact'

    id = Column('biofact_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    biocon_id = Column('biocon_id', Integer, ForeignKey(Bioconcept.id))
    biocon_type = Column('biocon_type', String)
    use_in_graph = Column('use_for_graph', String)

    bioentity = relationship(Bioentity, uselist=False, backref='biofacts')
    bioconcept = relationship(Bioconcept, uselist=False, backref='biofacts', cascade='all,delete')
    
    type = "BIOFACT"

    
    def __init__(self, bioent_id, biocon_id, biocon_type):
        self.bioent_id = bioent_id
        self.biocon_id = biocon_id
        self.biocon_type = biocon_type




    
