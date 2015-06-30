from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.contig import Contig
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.genomerelease import Genomerelease
from src.sgd.model.curate.locus import Locus
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.taxonomy import Taxonomy

__author__ = 'kelley'

class Dnasequenceannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'dnasequenceannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    dna_type = Column('dna_type', String)
    residues = Column('residues', CLOB)
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)
    start_index = Column('start_index', Integer)
    end_index = Column('end_index', Integer)
    strand = Column('strand', String)
    header = Column('header', String)
    filename = Column('filename', String)

    contig_id = Column('contig_id', Integer, ForeignKey(Contig.id))
    genomerelease_id = Column('genomerelease_id', Integer, ForeignKey(Genomerelease.id))

    #Relationships
    dbentity = relationship(Dbentity, uselist=False)
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    contig = relationship(Contig, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)

    __eq_values__ = ['id', 'bud_id', 'date_created', 'created_by',
                     'dna_type', 'residues', 'seq_version', 'coord_version', 'start_index', 'end_index', 'strand', 'header', 'filename']
    __eq_fks__ = [('dbentity', Dbentity, False),
                  ('source', Source, False),
                  ('taxonomy', Taxonomy, False),
                  ('contig', Contig, True),
                  ('genomerelease', Genomerelease, True),
                  ('extensions', 'dnasequenceannotation.Dnasequenceannotation_extension', True)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['taxonomy_id', 'dbentity_id', 'dna_type', 'seq_version', 'coord_version', 'strand', 'genomerelease_id', 'contig_id']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    @classmethod
    def create_or_find(cls, obj_json, session):
        if obj_json is None:
            return None

        dbentity, dbentity_status = Dbentity.create_or_find(obj_json['dbentity'], session)
        taxonomy, taxonomy_status = Taxonomy.create_or_find(obj_json['taxonomy'], session)

        if dbentity_status != 'Found':
            raise Exception('Dbentity not found: ' + str(obj_json['dbentity']))
        if taxonomy_status != 'Found':
            raise Exception('Taxonomy not found: ' + str(obj_json['taxonomy']))

        current_obj = session.query(cls)\
            .filter_by(dbentity_id=dbentity.id)\
            .filter_by(taxonomy_id=taxonomy.id)\
            .filter_by(dna_type=obj_json['dna_type']).first()

        if current_obj is None:
            return cls(obj_json, session), 'Created'
        else:
            return current_obj, 'Found'

class Dnasequenceannotation_extension(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'dnasequence_extension'

    id = Column('dnasequence_extension_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Dnasequenceannotation.id, ondelete='CASCADE'))
    display_name = Column('display_name', String)
    extension_type = Column('extension_type', String)
    relative_start_index = Column('relative_start_index', Integer)
    relative_end_index = Column('relative_end_index', Integer)
    chromosomal_start_index = Column('chromosomal_start_index', Integer)
    chromosomal_end_index = Column('chromosomal_end_index', Integer)
    phase = Column('phase', String)
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)
    genomerelease_id = Column('genomerelease_id', Integer, ForeignKey(Genomerelease.id))
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    annotation = relationship(Dnasequenceannotation, uselist=False, backref=backref('extensions', cascade="all, delete-orphan", passive_deletes=True))
    locus = relationship(Locus, uselist=False)
    genomerelease = relationship(Genomerelease, uselist=False)

    __eq_values__ = ['id', 'display_name', 'extension_type', 'relative_start_index', 'relative_end_index', 'chromosomal_start_index',
                     'chromosomal_end_index', 'phase', 'seq_version', 'coord_version',
                     'date_created', 'created_by']
    __eq_fks__ = [('annotation', Dnasequenceannotation, False),
                  ('locus', Locus, False),
                  ('genomerelease', Genomerelease, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.annotation is None else self.annotation.unique_key()), self.extension_type, self.relative_end_index, self.relative_end_index

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        current_obj = session.query(cls)\
            .filter_by(annotation_id=parent_obj.id)\
            .filter_by(extension_type=obj_json['extension_type'])\
            .filter_by(relative_start_index=obj_json['relative_start_index'])\
            .filter_by(relative_end_index=obj_json['relative_end_index']).first()

        if current_obj is None:
            return cls(obj_json, session), 'Created'
        else:
            return current_obj, 'Found'
