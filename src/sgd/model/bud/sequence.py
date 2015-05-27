from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB, Float

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from feature import Feature


class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'seq'

    id = Column('seq_no', Integer, primary_key = True)
    feature_id = Column('feature_no', String, ForeignKey(Feature.id))
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
    feature = relationship('Feature', backref='sequences')
    
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
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
    sequence_id = Column('seq_no', Integer, ForeignKey(Sequence.id))
    rootseq_id = Column('rootseq_no', Integer, ForeignKey(Sequence.id))
    coord_version = Column('coord_version', Date)
    min_coord = Column('min_coord', Integer)
    max_coord = Column('max_coord', Integer)
    strand = Column('strand', String)
    is_current = Column('is_current', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    sequence = relationship(Sequence, uselist=False, primaryjoin="Feat_Location.sequence_id==Sequence.id")
    feature = relationship(Feature, uselist=False, backref='feat_locations')

class Release(Base, EqualityByIDMixin):
    __tablename__ = 'release'

    id = Column('release_no', Integer, primary_key=True)
    organism_id = Column('organism_no', Integer)
    genome_release = Column('genome_release', String)
    sequence_release = Column('sequence_release', Float)
    annotation_release = Column('annotation_release', Float)
    curation_release = Column('curation_release', Float)
    filename = Column('tarball_file', String)
    release_date = Column('release_date', Date)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

class FeatLocation_Rel(Base, EqualityByIDMixin):
    __tablename__ = 'featloc_rel'

    id = Column('featloc_rel_no', Integer, primary_key=True)
    feature_location_id = Column('feat_location_no', Integer, ForeignKey(Feat_Location.id))
    release_id = Column('release_no', Integer, ForeignKey(Release.id))

    feature_location = relationship(Feat_Location, uselist=False, backref='featlocation_rels')
    release = relationship(Release, uselist=False)

class ProteinInfo(Base, EqualityByIDMixin):
    __tablename__ = 'protein_info'
    
    id = Column('protein_info_no', Integer, primary_key=True)
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))
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
    
    feature = relationship(Feature, uselist=False)
    
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
    info_id = Column('protein_info_no', Integer, ForeignKey(ProteinInfo.id))
    group = Column('protein_detail_group', String)
    type = Column('protein_detail_type', String)
    value = Column('protein_detail_value', String)
    min_coord = Column('min_coord', Integer)
    max_coord = Column('max_coord', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    info = relationship(ProteinInfo, uselist=False, backref='details')