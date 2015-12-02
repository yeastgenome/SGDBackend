from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB, Numeric
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.so import So
from src.sgd.model.nex.contig import Contig
# from src.sgd.model.nex.file import File
from src.sgd.model.nex.genomerelease import Genomerelease

__author__ = 'sweng66'

class Dnasequenceannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'dnasequenceannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    bud_id = Column('bud_id', Integer)
    so_id = Column('so_id', Integer, ForeignKey(So.id))
    dna_type = Column('dna_type', String)
    contig_id = Column('contig_id', Integer, ForeignKey(Contig.id))
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)
    genomerelease_id = Column('genomerelease_id', Integer, ForeignKey(Genomerelease.id))
    start_index = Column('start_index', Integer)
    end_index= Column('end_index', Integer)
    strand = Column('strand', String)
    file_header = Column('file_header', String)
    download_filename = Column('download_filename', String)
    # file_id = Column('file_id', Integer, ForeignKey(File.id))   
    file_id = Column('file_id', Integer)
    residues = Column('residues', CLOB)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    so = relationship(So, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    # file = relationship(File, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)

    __eq_values__ = ['id', 'dbentity_id', 'taxonomy_id', 'reference_id', 'bud_id', 
                     'so_id', 'dna_type', 'contig_id', 'seq_version', 'coord_version',
                     'genomerelease_id', 'start_index', 'end_index', 'strand', 'file_header',
                     'download_filename', 'file_id', 'residues', 'date_created', 'created_by']
    # ('file', File, False),
    __eq_fks__ = [('source', Source, False),
                  ('so', So, False),
                  ('taxonomy', Taxonomy, False),
                  ('dbentity', Dbentity, True),
                  ('genomerelease', Genomerelease, False),
                  ('reference', Reference, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['seq_version', 'coord_version', 'taxonomy_id', 'so_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

