from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date

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
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    
    __eq_values__ = ['id', 'username', 'first_name', 'last_name', 'email', 'status', 'bud_id', 'date_created']
    __eq_fks__ = []
    # __id_values__ = ['id', 'username']
    __id_values__ = ['id'] 
    # __no_edit_values__ = ['id', 'username', 'date_created']
    __no_edit_values__ = ['username']   
    __filter_values__ = []
    
    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)
