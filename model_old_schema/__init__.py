from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

Base = declarative_base()
metadata = Base.metadata
current_user = None