from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean
# from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, String, Text, text, FetchedValue
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin

__author__ = 'sweng66'

class Dbuser(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'dbuser'

    id = Column('dbuser_id', Integer, primary_key=True)
    username = Column('username', String)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    email = Column('email', String)
    status = Column('status', String)
    is_curator = Column('is_curator', Boolean)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    
    __eq_values__ = ['id', 'username', 'first_name', 'last_name', 'status', 'is_curator', 'date_created']
    __eq_fks__ = []
    __id_values__ = ['id', 'username']
    __no_edit_values__ = ['id', 'username', 'date_created']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.email = obj_json['email']
        UpdateWithJsonMixin.__init__(self, obj_json, session)
