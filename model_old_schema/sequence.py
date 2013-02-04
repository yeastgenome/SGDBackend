'''
Created on Oct 25, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Sequence module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date


class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'seq'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('seq_no', Integer, primary_key = True)
    feature_id = Column('feature_no', String, ForeignKey('bud.feature.feature_no'))
    version = Column('seq_version', Date)
    type = Column('seq_type', String)
    is_current = Column('is_current', String)
    length = Column('seq_length', Integer)
    ftp_file = Column('ftp_file', String)
    residues = Column('residues', String)
        
    def __repr__(self):
        data = self.length, self.type, self.is_current
        return 'Sequence(length=%s, type=%s, is_current=%s)' % data
    