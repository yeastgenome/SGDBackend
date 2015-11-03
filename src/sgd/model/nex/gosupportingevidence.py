from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.ro import Ro
from src.sgd.model.nex.goannotation import Goannotation

__author__ = 'sweng66'

class Gosupportingevidence(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'gosupportingevidence'

    id = Column('gosupportingevidence_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Goannotation.id, ondelete='CASCADE'))
    link = Column('obj_url', String)
    group_id = Column('group_id', Integer)
    dbxref_id = Column('dbxref_id', String)
    evidence_type = Column('evidence_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships                 
    annotation = relationship(Goannotation, uselist=False, backref=backref('gosupportingevidences', cascade="all, delete-orphan", passive_deletes=True))

    __eq_values__ = ['id', 'annotation_id', 'link', 'group_id', 'evidence_type', 'dbxref_id']
    __eq_fks__ = []
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)



