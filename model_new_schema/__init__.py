from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData


Base = declarative_base()
metadata = MetaData()

def subclasses(cls):
    return map(lambda x: x.__mapper_args__['polymorphic_identity'], cls.__subclasses__())

def plural_to_singular(plural):
    if plural.endswith('ies'):
        return plural[:-3] + 'y'
    elif plural.endswith('es'):
        return plural[:-2]
    elif plural.endswith('s'):
        return plural[:-1]
    else:
        return plural