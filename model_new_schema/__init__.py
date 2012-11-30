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
    
class CommonEqualityMixin(object):
    def __eq__(self, other):
        if type(other) is type(self):
            return reduce(lambda x, y: x and (y == '_sa_instance_state' or self.__dict__[y] == other.__dict__[y]), self.__dict__.keys(), True)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)