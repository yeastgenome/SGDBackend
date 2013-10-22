from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

class EqualityByIDMixin(object):
    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
def create_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

SCHEMA = None  
Base = None
metadata = None


