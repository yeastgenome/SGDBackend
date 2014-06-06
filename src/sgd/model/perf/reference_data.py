from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from core import Reference
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'
class ReferenceDetails(Base, EqualityByIDMixin):
    __tablename__ = 'reference_details'

    id = Column('reference_details_id', Integer, primary_key=True)
    obj_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, reference_id, class_type, json):
        self.obj_id = reference_id
        self.class_type = class_type
        self.json = json