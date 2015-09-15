from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.colleague import Colleague
from src.sgd.model.nex.keyword import Keyword

__author__ = 'sweng66'

class ColleagueKeyword(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_keyword'

    id = Column('colleague_keyword_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    keyword_id = Column('keyword_id', Integer, ForeignKey(Keyword.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    
    __eq_values__ = ['id', 'colleague_id', 'keyword_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.colleague_id = obj_json['colleague_id']
        self.keyword_id = obj_json['keyword_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.colleague_id, self.keyword_id

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json

        

