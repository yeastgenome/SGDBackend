from sgdbackend.config import SCHEMA
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import model_new_schema




DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
class Base(object):
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

model_new_schema.SCHEMA = SCHEMA
model_new_schema.Base = declarative_base(cls=Base)