'''
Created on Mar 22, 2013

@author: kpaskov
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.bioentity import Bioentity
from model_new_schema.evelement import Strain
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, CLOB, Float


class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'seq'

    id = Column('seq_id', Integer, primary_key = True)
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
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    seq_tags = relationship('Seqtag')
    strain = relationship('Strain')
    bioent = relationship('Bioentity', uselist=False, backref='sequences')
            
    def __init__(self, bioent_id, seq_version, coord_version, min_coord, max_coord, strand, length,
                 ftp_file, residues, seq_type, source, rootseq_id, strain_id,
                 session=None, sequence_id=None, date_created=None, created_by=None):
        self.bioent_id = bioent_id
        self.seq_version = seq_version
        self.coord_version = coord_version
        self.min_coord = min_coord
        self.max_coord = max_coord
        self.strand = strand
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
    secondary_name = Column('secondary_name', String)
    relative_coord = Column('relative_coord', Integer)
    chrom_coord = Column('chrom_coord', Integer)
    length = Column('length', Integer)
    orf_classification = Column('orf_classification', String)
    score = Column('score', Float)
    strand = Column('strand', String)
    frame = Column('frame', Integer)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    def __init__(self, seq_id, name, seqtag_type, dbxref_id, source, secondary_name, 
                 relative_coord, chrom_coord, length, 
                 score, strand, frame, orf_classification,
                 session=None, seqtag_id=None, date_created=None, created_by=None):
        self.seq_id = seq_id
        self.name = name
        self.seqtag_type = seqtag_type
        self.dbxref_id = dbxref_id
        self.source = source
        self.secondary_name = secondary_name
        self.relative_coord = relative_coord
        self.chrom_coord = chrom_coord
        self.length = length
        
        if session is None:
            self.id = seqtag_id
            self.date_created = date_created
            self.created_by = created_by
            
class Assembly(Base, EqualityByIDMixin):
    __tablename__ = 'assembly'
    
    id = Column('assembly_id', Integer, primary_key = True)
    name = Column('name', String)
    description = Column('description', String)
    filename = Column('filename', String)
    coverage = Column('coverage', String)
    mean_contig_size = Column('mean_contig_size', Integer)
    n50 = Column('n50', Integer)
    num_gene_features = Column('num_gene_features', Integer)
    software = Column('software', String)
    strain_id = Column('strain_id', String)
    background_strain_id = Column('background_strain_id', String)
    
    def __init__(self, name, description, filename, coverage, mean_contig_size, n50, num_gene_features, software, strain_id, background_strain_id,
                 assembly_id=None):
        self.name = name
        self.description = description
        self.filename = filename
        self.coverage = coverage
        self.mean_contig_size = mean_contig_size
        self.n50 = n50
        self.num_gene_features = num_gene_features
        self.software = software
        self.strain_id = strain_id
        self.background_strain_id = background_strain_id
        
        self.id = assembly_id
        

    
    
        
    
    
        