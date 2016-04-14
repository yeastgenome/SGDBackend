from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB, Numeric
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.colleague import Colleague

__author__ = 'sweng66'

class Reservedname(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'reservedname'

    id = Column('reservedname_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id))
    reservation_date = Column('reservation_date', Date, server_default=FetchedValue())
    expiration_date = Column('expiration_date', Date, server_default=FetchedValue())
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    locus = relationship(Locus, uselist=False)
    reference = relationship(Reference, uselist=False)
    colleague = relationship(Colleague, uselist=False)
    
    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'locus_id', 
                     'reference_id', 'colleague_id', 'reservation_date', 'expiration_date',
                     'description', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('locus', Locus, False),
                  ('reference', Reference, False),
                  ('colleague', Colleague, False)]
    __id_values__ = ['id', 'display_name', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['colleague_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

