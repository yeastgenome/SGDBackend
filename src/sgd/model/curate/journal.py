from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Journal(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'journal'

    id = Column('journal_id', String, primary_key = True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    title = Column('title', String)
    med_abbr = Column('med_abbr', String)
    issn_print = Column('issn_print', String)
    issn_online = Column('issn_online', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'bud_id', 'link', 'title', 'med_abbr', 'issn_print', 'issn_online',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.title, self.med_abbr

    @classmethod
    def __create_name__(cls, obj_json):
        if 'title' in obj_json:
            return obj_json['title']
        else:
            return obj_json['med_abbr']

    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['title'] = self.title
        obj_json['med_abbr'] = self.med_abbr
        return obj_json

    @classmethod
    def specialized_find(cls, obj_json, session):
        return session.query(cls).\
            filter_by(title=None if 'title' not in obj_json else obj_json['title']).\
            filter_by(med_abbr=None if 'med_abbr' not in obj_json else obj_json['med_abbr']).first()

