from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.colleague import Colleague

__author__ = 'sweng66'

class ColleagueAssociation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_association'

    id = Column('colleague_association_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    associate_id = Column('associate_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    association_type = Column('association_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    
    __eq_values__ = ['id', 'colleague_id', 'associate_id', 'association_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.colleague_id = obj_json['colleague_id']
        self.associate_id = obj_json['associate_id']
        self.association_type = obj_json['association_type']
        self.bud_id = obj_json['bud_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.colleague_id, self.associate_id, self.association_type

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json

        

