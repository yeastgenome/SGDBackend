from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB, Numeric
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.so import So
# from src.sgd.model.nex.file import File
from src.sgd.model.nex.genomerelease import Genomerelease

__author__ = 'sweng66'

class ArchContig(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'arch_contig'

    id = Column('contig_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    so_id = Column('so_id', Integer, ForeignKey(So.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    residues = Column('residues', CLOB)
    taxonomy_id = Column('taxonomy_id', ForeignKey(Taxonomy.id))
    reference_chromosome_id = Column('reference_chromosome_id', Integer, ForeignKey('nex.arch_contig.contig_id'))
    centromere_start = Column('centromere_start', Integer)
    centromere_end = Column('centromere_end', Integer)
    genbank_accession = Column('genbank_accession', String)
    gi_number = Column('gi_number', String)
    refseq_id = Column('refseq_id', String)
    reference_start = Column('reference_start', Integer)
    reference_end = Column('reference_end', Integer)
    reference_percent_identity = Column('reference_percent_identity', Numeric(7, 3))
    reference_alignment_length = Column('reference_alignment_length', Integer)
    file_header = Column('file_header', String)
    download_filename = Column('download_filename', String)
    # file_id = Column('file_id', Integer, ForeignKey(File.id))
    file_id = Column('file_id', Integer)
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)
    genomerelease_id = Column('genomerelease_id', Integer, ForeignKey(Genomerelease.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_archived = Column('date_archived', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    so = relationship(So, uselist=False)
    # file = relationship(File, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False, backref='arch_contigs')
    reference_chromosome = relationship('ArchContig', remote_side=[id])

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'residues', 
                     'centromere_start', 'centromere_end', 'download_filename', 'taxonomy_id',
                     'genbank_accession', 'gi_number', 'refseq_id', 'file_header', 
                     'file_id', 'reference_start', 'reference_end', 'reference_percent_identity', 
                     'reference_alignment_length', 'seq_version', 'coord_version', 
                     'genomerelease_id', 'so_id', 'date_created', 'created_by', 'date_archived']
    # ('file', File, False),
    __eq_fks__ = [('source', Source, False),
                  ('so', So, False),
                  ('taxonomy', Taxonomy, False),
                  ('genomerelease', Genomerelease, False),
                  ('reference_chromosome', 'arch_contig.ArchContig', False)]
    __id_values__ = ['id', 'display_name', 'genbank_accession', 'gi_number', 'refseq_id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by', 'date_archived']
    __filter_values__ = ['reference_chromosome_id', 'seq_version', 'coord_version', 'taxonomy_id', 'so_id']

    def __init__(self, obj_json, session):
        self.taxonomy_id = obj_json['taxonomy_id']
        self.format_name = obj_json['format_name']
        self.display_name = obj_json['display_name']
        self.seq_version = obj_json['seq_version']
        self.coord_version = obj_json.get('coord_version')
        self.genomerelease_id = obj_json['genomerelease_id']
        self.file_header = obj_json['file_header']
        self.download_filename = obj_json['download_filename']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.format_name



