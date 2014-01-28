__author__ = 'kpaskov'

from model_perf_schema import EqualityByIDMixin, Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String
from core import Reference

class ReferenceDetails(Base, EqualityByIDMixin):
    __tablename__ = 'reference_details'

    id = Column('reference_details_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, reference_id, class_type, json):
        self.reference_id = reference_id
        self.class_type = class_type
        self.json = json