from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Journal(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'journal'

    id = Column('journal_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    title = Column('title', String)
    med_abbr = Column('med_abbr', String)
    issn_print = Column('issn_print', String)
    issn_online = Column('issn_electronic', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'bud_id', 'link', 'title', 'med_abbr', 'issn_print', 'issn_online',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.title, self.med_abbr

    @classmethod
    def __create_display_name__(cls, obj_json):
        return obj_json['title'] if 'title' in obj_json else obj_json['med_abbr']

    @classmethod
    def __create_format_name__(self, obj_json):
        if 'med_abbr' in obj_json and 'title' in obj_json:
            return create_format_name(obj_json['title'][0:50] + obj_json['med_abbr'][0:50])
        elif 'med_abbr' in obj_json:
            return create_format_name(obj_json['med_abbr'][0:100])
        elif 'title' in obj_json:
            return create_format_name(obj_json['title'][:100])
        else:
            raise Exception('Journal must have med_abbr or title.')

