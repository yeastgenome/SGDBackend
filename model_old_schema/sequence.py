'''
Created on Oct 25, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Sequence module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB


class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'seq'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('seq_no', Integer, primary_key = True)
    feature_id = Column('feature_no', String, ForeignKey('bud.feature.feature_no'))
    seq_version = Column('seq_version', Date)
    seq_type = Column('seq_type', String)
    source = Column('source', String)
    is_current = Column('is_current', String)
    seq_length = Column('seq_length', Integer)
    ftp_file = Column('ftp_file', String)
    residues = Column('residues', CLOB)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    feat_locations = relationship('Feat_Location', primaryjoin="Feat_Location.sequence_id==Sequence.id", lazy='joined')
    
    
    @hybrid_property
    def current_feat_location(self):
        current = [ofl for ofl in self.feat_locations if ofl.is_current == 'Y']
        if len(current) > 0:
            return current[0]
        else:
            return None
        
    def __repr__(self):
        data = self.length, self.type, self.is_current
        return 'Sequence(length=%s, type=%s, is_current=%s)' % data
    
class Feat_Location(Base, EqualityByIDMixin):
    __tablename__ = 'feat_location'
    
    id = Column('feat_location_no', Integer, primary_key=True)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    sequence_id = Column('seq_no', Integer, ForeignKey('bud.seq.seq_no'))
    rootseq_id = Column('rootseq_no', Integer, ForeignKey('bud.seq.seq_no'))
    coord_version = Column('coord_version', Date)
    min_coord = Column('min_coord', Integer)
    max_coord = Column('max_coord', Integer)
    strand = Column('strand', String)
    is_current = Column('is_current', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    

    