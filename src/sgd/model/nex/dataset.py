from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, Float, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import ToJsonMixin, UpdateWithJsonMixin, Base
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.file import File
from src.sgd.model.nex.obi import Obi
from src.sgd.model.nex.keyword import Keyword

__author__ = 'sweng66'

class Dataset(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'dataset'

    id = Column('dataset_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    dbxref_id = Column('dbxref_id', String)
    dbxref_type = Column('dbxref_type', String)
    assay_id = Column('assay_id', Integer, ForeignKey(Obi.id))
    channel_count = Column('channel_count', Integer)
    sample_count = Column('sample_count', Integer)
    description = Column('description', String)
    is_in_spell = Column('is_in_spell', Integer)
    is_in_browser = Column('is_in_browser', Integer)
    parent_dataset_id = Column('parent_dataset_id', Integer)
    date_public = Column('date_public', Date, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'dbxref_id',
                     'dbxref_type', 'assay_id', 'channel_count', 
                     'sample_count', 'description', 'is_in_spell', 'is_in_browser',
                     'parent_dataset_id', 'date_public', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['assay_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)




