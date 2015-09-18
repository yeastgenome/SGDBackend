from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.colleague import Colleague

__author__ = 'sweng66'

class ColleagueUrl(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'colleague_url'

    id = Column('url_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id))
    bud_id = Column('bud_id', Integer)
    url_type = Column('url_type', String)
    link = Column('obj_url', String)
    display_name = Column('display_name', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'url_type', 'colleague_id', 'link', 'bud_id', 'created_by', 'date_created']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.colleague_id = obj_json['colleague_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.colleague_id, self.display_name, self.url_type, self.link

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json

    def to_semi_json(self):
        return self.to_min_json()

