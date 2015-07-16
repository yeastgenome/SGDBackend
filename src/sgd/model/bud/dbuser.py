from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base

class Dbuser(Base, EqualityByIDMixin):
    __tablename__ = 'dbuser'

    id = Column('dbuser_no', Integer, primary_key = True)
    username = Column('userid', String)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    status = Column('status', String)
    email = Column('email', String)
    date_created = Column('date_created', Date)

    def __repr__(self):
        data = self.username, self.first_name, self.last_name, self.email
        return 'Dbuser(username=%s, first_name=%s, last_name=%s, email=%s)' % data

