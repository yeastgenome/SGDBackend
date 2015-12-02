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

class Contig(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'contig'

    id = Column('contig_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    so_id = Column('so_id', Integer, ForeignKey(So.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    residues = Column('residues', CLOB)
    taxonomy_id = Column('taxonomy_id', ForeignKey(Taxonomy.id))
    reference_chromosome_id = Column('reference_chromosome_id', Integer, ForeignKey('nex.contig.contig_id'))
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
    # description = Column('description', String) 
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    so = relationship(So, uselist=False)
    # file = relationship(File, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False, backref='contigs')
    reference_chromosome = relationship('Contig', remote_side=[id])

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'residues', 
                     'centromere_start', 'centromere_end', 'download_filename', 'taxonomy_id',
                     'genbank_accession', 'gi_number', 'refseq_id', 'file_header', 
                     'file_id', 'reference_start', 'reference_end', 'reference_percent_identity', 
                     'reference_alignment_length', 'seq_version', 'coord_version', 
                     'genomerelease_id', 'so_id', 'date_created', 'created_by']
    # ('file', File, False),
    __eq_fks__ = [('source', Source, False),
                  ('so', So, False),
                  ('taxonomy', Taxonomy, False),
                  ('urls', 'contig.ContigUrl', True),
                  ('genomerelease', Genomerelease, False),
                  ('reference_chromosome', 'contig.Contig', False)]
    __id_values__ = ['id', 'display_name', 'genbank_accession', 'gi_number', 'refseq_id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['reference_chromosome_id', 'seq_version', 'coord_version', 'taxonomy_id', 'so_id']

    def __init__(self, obj_json, session):
        self.taxonomy_id = obj_json['taxonomy_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_display_name__(cls, obj_json):
        return obj_json['genbank_accession'] if 'display_name' not in obj_json else obj_json['display_name']

class ContigUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'contig_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    contig_id = Column('contig_id', Integer, ForeignKey(Contig.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    contig = relationship(Contig, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('contig', Contig, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.contig is None else self.contig.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.contig_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(contig_id=newly_created_object.contig_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


