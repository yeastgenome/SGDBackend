from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
#from src.sgd.model.nex.colleague import Colleague
#from src.sgd.model.nex.dataset import Dataset

__author__ = 'kelley'

class Keyword(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'keyword'

    id = Column('keyword_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    source = relationship(Source, uselist=False, lazy='joined')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'description', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        #obj_json['datasets'] = [x.dataset.to_semi_json() for x in self.dataset_keywords]
        obj_json['colleagues'] = [x.colleague.to_min_json() for x in self.colleague_keywords]
        return obj_json


class DatasetKeyword(Base, EqualityByIDMixin, ToJsonMixin):
    __tablename__ = 'dataset_keyword'

    id = Column('dataset_keyword_id', Integer, primary_key=True)
    keyword_id = Column('keyword_id', Integer, ForeignKey(Keyword.id))
    #dataset_id = Column('dataset_id', Integer, ForeignKey(Colleague.id))

    #Relationships
    keyword = relationship(Keyword, uselist=False, backref=backref('dataset_keywords', passive_deletes=True))
    #dataset = relationship(Colleague, uselist=False, backref=backref('dataset_keywords', passive_deletes=True))

    __eq_values__ = ['id']
    __eq_fks__ = ['keyword', 'dataset']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.keyword_id, self.dataset_id