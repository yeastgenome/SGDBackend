'''
Created on Oct 25, 2012

@author: kpaskov

These classes are populated using SQLAlchemy to connect to the BUD schema on Fasolt. These are the classes representing tables in the
Sequence module of the database schema.
'''
from model_old_schema import Base, EqualityByIDMixin, SCHEMA
from model_old_schema.feature import Feature
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB, Float


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
    
    feat_locations = relationship('Feat_Location', primaryjoin="Feat_Location.sequence_id==Sequence.id")
    
    @hybrid_property
    def current_feat_location(self):
        current = [ofl for ofl in self.feat_locations if ofl.is_current == 'Y']
        if len(current) > 0:
            return current[0]
        else:
            return None
        
    def __repr__(self):
        data = self.id, self.seq_type, self.is_current
        return 'Sequence(id=%s, type=%s, is_current=%s)' % data
    
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
    
class ProteinInfo(Base, EqualityByIDMixin):
    __tablename__ = 'protein_info'
    
    id = Column('protein_info_no', Integer, primary_key=True)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    molecular_weight = Column('molecular_weight', Integer)
    pi = Column('pi', Float)
    cai = Column('cai', Float)
    length = Column('protein_length', Integer)
    n_term_seq = Column('n_term_seq', String)
    c_term_seq = Column('c_term_seq', String)
    codon_bias = Column('codon_bias', Float)
    fop_score = Column('fop_score', Float)
    gravy_score = Column('gravy_score', Float)
    aromaticity_score = Column('aromaticity_score', Float)
    
    details = relationship('ProteinDetail')
    feature = relationship('Feature')
    
    ala = Column('ala', Integer)
    arg = Column('arg', Integer)
    asn = Column('asn', Integer)
    asp = Column('asp', Integer)
    cys = Column('cys', Integer)
    gln = Column('gln', Integer)
    glu = Column('glu', Integer)
    gly = Column('gly', Integer)
    his = Column('his', Integer)
    ile = Column('ile', Integer)
    leu = Column('leu', Integer)
    lys = Column('lys', Integer)
    met = Column('met', Integer)
    phe = Column('phe', Integer)
    pro = Column('pro', Integer)
    thr = Column('thr', Integer)
    ser = Column('ser', Integer)
    trp = Column('trp', Integer)
    tyr = Column('tyr', Integer)
    val = Column('val', Integer)
    
class ProteinDetail(Base, EqualityByIDMixin):
    __tablename__ = 'protein_detail'
    
    id = Column('protein_detail_no', Integer, primary_key=True)
    info_id = Column('protein_info_no', Integer, ForeignKey('bud.protein_info.protein_info_no'))
    group = Column('protein_detail_group', String)
    type = Column('protein_detail_type', String)
    value = Column('protein_detail_value', String)
    min_coord = Column('min_coord', Integer)
    max_coord = Column('max_coord', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    