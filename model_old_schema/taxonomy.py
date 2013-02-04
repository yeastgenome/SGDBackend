'''
Created on Oct 24, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Taxonomy module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

class Taxonomy(Base, EqualityByIDMixin):
    __tablename__ = 'taxonomy'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('taxon_id', Integer, primary_key = True)
    name = Column('tax_term', String)
    common_name = Column('common_name', String)
    rank = Column('rank', String)
    
    def __repr__(self):
        data = self.name, self.common_name, self.rank
        return 'Taxonomy(name=%s, common_name=%s, rank=%s)' % data