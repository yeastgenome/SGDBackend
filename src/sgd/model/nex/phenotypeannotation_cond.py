from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.phenotypeannotation import Phenotypeannotation

__author__ = 'sweng66'

class PhenotypeannotationCond(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'phenotypeannotation_cond'

    id = Column('condition_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Phenotypeannotation.id, ondelete='CASCADE'))
    condition_class = Column('condition_class', String)
    condition_name = Column('condition_name', String)
    condition_value = Column('condition_value', String)
    condition_unit = Column('condition_unit', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships                                                               
                                                            
    annotation = relationship(Phenotypeannotation)

    __eq_values__ = ['id', 'annotation_id', 'condition_class', 'condition_name', 'condition_value', 'condition_unit', 'date_created', 'created_by']
    __eq_fks__ = []
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)



