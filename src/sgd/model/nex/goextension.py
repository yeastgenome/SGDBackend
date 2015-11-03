from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.ro import Ro
from src.sgd.model.nex.goannotation import Goannotation

__author__ = 'sweng66'

class Goextension(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'goextension'

    id = Column('goextension_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Goannotation.id, ondelete='CASCADE'))
    link = Column('obj_url', String)
    group_id = Column('group_id', Integer)
    dbxref_id = Column('dbxref_id', String)
    ro_id = Column('ro_id', Integer, ForeignKey(Ro.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships                                                               
                                                            
    annotation = relationship(Goannotation, uselist=False, backref=backref('goextensions', cascade="all, delete-orphan", passive_deletes=True))
    ro = relationship('Ro')
    role = association_proxy('ro', 'display_name')

    __eq_values__ = ['id', 'annotation_id', 'link', 'group_id', 'ro_id', 'dbxref_id']
    __eq_fks__ = []
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.annotation_id = obj_json['annotation_id'] 
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    # def __init__(self, obj_json, session):
    #    self.annotation_id = obj_json['annotation_id']
    #    self.update(obj_json, session)


