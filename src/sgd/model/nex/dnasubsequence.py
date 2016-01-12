from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB, Numeric
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.so import So
from src.sgd.model.nex.dnasequenceannotation import Dnasequenceannotation
# from src.sgd.model.nex.file import File
from src.sgd.model.nex.genomerelease import Genomerelease

__author__ = 'sweng66'

class Dnasubsequence(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'dnasubsequence'

    id = Column('dnasubsequence_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Dnasequenceannotation.id))
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    display_name = Column('display_name', String)
    bud_id = Column('bud_id', Integer)
    so_id = Column('so_id', Integer, ForeignKey(So.id))
    relative_start_index = Column('relative_start_index', Integer)
    relative_end_index = Column('relative_end_index', Integer)
    contig_start_index = Column('contig_start_index', Integer)
    contig_end_index = Column('contig_end_index', Integer)
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)
    genomerelease_id = Column('genomerelease_id', Integer, ForeignKey(Genomerelease.id))
    file_header = Column('file_header', String)
    download_filename = Column('download_filename', String)
    # file_id = Column('file_id', Integer, ForeignKey(File.id))   
    file_id = Column('file_id', Integer)
    residues = Column('residues', CLOB)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    so = relationship(So, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    # file = relationship(File, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)

    __eq_values__ = ['id', 'annotation_id', 'dbentity_id', 'display_name', 'bud_id', 
                     'so_id', 'relative_start_index', 'relative_end_index', 
                     'contig_start_index', 'contig_end_index', 'seq_version', 'coord_version',
                     'genomerelease_id', 'file_header', 'download_filename', 'file_id', 
                     'residues', 'date_created', 'created_by']
    # ('file', File, False),
    __eq_fks__ = [('so', So, False),
                  ('dbentity', Dbentity, True),
                  ('genomerelease', Genomerelease, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['seq_version', 'coord_version', 'so_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

