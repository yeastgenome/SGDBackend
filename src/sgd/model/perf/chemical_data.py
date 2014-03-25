from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, CLOB, String

from src.sgd.model.perf import Base
from core import Chemical
from src.sgd.model import EqualityByIDMixin


__author__ = 'kpaskov'

class ChemicalDetails(Base, EqualityByIDMixin):
    __tablename__ = 'chemical_details'

    id = Column('chemical_details_id', Integer, primary_key=True)
    chemical_id = Column('chemical_id', Integer, ForeignKey(Chemical.id))
    class_type = Column('class', String)
    json = Column('json', CLOB)

    def __init__(self, chemical_id, class_type, json):
        self.chemical_id = chemical_id
        self.class_type = class_type
        self.json = json
