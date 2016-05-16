from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, Float, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import ToJsonMixin, UpdateWithJsonMixin, Base
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.filepath import Filepath
from src.sgd.model.nex.edam import Edam

__author__ = 'sweng66'

class File(Dbentity):
    __tablename__ = 'filedbentity'

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)
    md5sum = Column('md5sum', String)
    previous_file_name = Column('previous_file_name', String)
    data_id = Column('data_id', Integer, ForeignKey(Edam.id))
    format_id = Column('format_id', Integer, ForeignKey(Edam.id))
    file_date = Column('file_date', Date, server_default=FetchedValue())
    is_public = Column('is_public', Integer)
    is_in_spell = Column('is_in_spell', Integer)
    is_in_browser = Column('is_in_browser', Integer)
    filepath_id = Column('filepath_id', Integer, ForeignKey(Filepath.id))
    file_extension = Column('file_extension', String)
    s3_url = Column('s3_url', String)
    topic_id = Column('topic_id', Integer, ForeignKey(Edam.id))
    readme_file_id = Column('readme_file_id', Integer)
    description = Column('description', String)

    #Relationships
    filepath = relationship(Filepath, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'FILE', 'inherit_condition': id == Dbentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'date_created', 
                     'created_by', 'sgdid', 'dbentity_status', 'md5sum', 'previous_file_name',
                     'data_id', 'format_id', 'file_date', 'is_public', 'is_in_spell', 
                     'is_in_browser', 'filepath_id', 'file_extension', 's3_url', 'topic_id',
                     'readme_file_id', 'description']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['filepath_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

