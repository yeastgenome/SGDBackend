from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date, Float

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Genomerelease(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'genomerelease'

    id = Column('genomerelease_id', String, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    name = Column('name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    genome_release = Column('genome_release', String)
    sequence_release = Column('sequence_release', Float)
    annotation_release = Column('annotation_release', Float)
    curation_release = Column('curation_release', Float)
    filename = Column('filename', String)
    release_date = Column('release_date', Date)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'description', 'bud_id', 'date_created', 'created_by',
                     'genome_release', 'sequence_release', 'annotation_release', 'curation_release', 'filename', 'release_date']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'name', 'genome_release']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = ['sequence_release', 'annotation_release', 'curation_release']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_name__(cls, obj_json):
        return obj_json['genome_release']

    def unique_key(self):
        return self.genome_release
