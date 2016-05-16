from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.keyword import Keyword
from src.sgd.model.nex.file import File

__author__ = 'sweng66'

class FileKeyword(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'file_keyword'

    id = Column('file_keyword_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    keyword_id = Column('keyword_id', Integer, ForeignKey(Keyword.id, ondelete='CASCADE'))
    file_id = Column('file_id', Integer, ForeignKey(File.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    
    __eq_values__ = ['id', 'keyword_id', 'file_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.keyword_id, self.file_id

        

