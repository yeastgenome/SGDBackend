__author__ = 'kpaskov'

from model_new_schema import Base, EqualityByIDMixin
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric

class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'sequence'

    id = Column('sequence_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type}

    def __init__(self, display_name, format_name, class_type,
                 date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.format_name, self.class_type)