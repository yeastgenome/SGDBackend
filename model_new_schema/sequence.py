'''
Created on Mar 22, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioentity import Bioentity
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB


class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'seq'

    id = Column('sequence_id', Integer, primary_key = True)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)
    min_coord = Column('min_coord', Integer)
    max_coord = Column('max_coord', Integer)
    strand = Column('strand', String)
    is_current = Column('is_current', String)
    length = Column('length', Integer)
    ftp_file = Column('ftp_file', String)
    residues = Column('residues', CLOB)
    seq_type = Column('seq_type', String)
    source = Column('source', String)
    rootseq_id = Column('rootseq_id', Integer)
    strain_id = Column('strain_id', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    @hybrid_property
    def formatted_residues(self):
        if self.seq_type == 'genomic':
            return  ' '.join(self.residues[i:i+3] for i in range(0, len(self.residues), 3)) + ' '
            #return self.residues
        else:
            return self.residues
            
    def __init__(self, bioent_id, seq_version, coord_version, min_coord, max_coord, strand, is_current, length,
                 ftp_file, residues, seq_type, source, rootseq_id, strain_id,
                 session=None, sequence_id=None, date_created=None, created_by=None):
        self.bioent_id = bioent_id
        self.seq_version = seq_version
        self.coord_version = coord_version
        self.min_coord = min_coord
        self.max_coord = max_coord
        self.strand = strand
        self.is_current = is_current
        self.length = length
        self.ftp_file = ftp_file
        self.residues = residues
        self.seq_type = seq_type
        self.source = source
        self.rootseq_id = rootseq_id
        self.date_created = date_created
        self.created_by = created_by
        self.strain_id = strain_id
        
        if session is None:
            self.id = sequence_id
            self.date_created = date_created
            self.created_by = created_by
            
class Seqtag(Base, EqualityByIDMixin):
    __tablename__ = 'seqtag'
    
    id = Column('seqtag_id', Integer, primary_key = True)
    seq_id = Column('seq_id', Integer, ForeignKey(Sequence.id))
    name = Column('name', String)
    seqtag_type = Column('seqtag_type', String)
    dbxref_id = Column('dbxref', String)
    source = Column('source', String)
    status = Column('status', String)
    secondary_name = Column('secondary_name', String)
    relative_coord = Column('relative_coord', Integer)
    chrom_coord = Column('chrom_coord', Integer)
    length = Column('length', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, seq_id, name, seqtag_type, dbxref_id, source, status, secondary_name, 
                 relative_coord, chrom_coord, length, 
                 session=None, seqtag_id=None, date_created=None, created_by=None):
        self.seq_id = seq_id
        self.name = name
        self.seqtag_type = seqtag_type
        self.dbxref_id = dbxref_id
        self.source = source
        self.status = status
        self.secondary_name = secondary_name
        self.relative_coord = relative_coord
        self.chrom_coord = chrom_coord
        self.length = length
        
        if session is None:
            self.id = seqtag_id
            self.date_created = date_created
            self.created_by = created_by
        
    
    
        