from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.reference import Reference
from src.sgd.model.curate.locus import Locus
from src.sgd.model.curate.colleague import Colleague


__author__ = 'kkarra'

class Reservedname(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'reservedname'

    id = Column('reservedname_id', Integer, primary_key=True)
    source_id = Column('source_id',Integer, ForeignKey(Source.id))
    reference_id = Column('reference_id', ForeignKey(Reference.id))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id))
    bud_id = Column('bud_id', Integer)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    reservation_date = Column('reservation_date', Date, server_default=FetchedValue())
    expiration_date = Column('expiration_date', Date, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    created_by = Column('created_by', String)
    link = Column('object_url', String)

    #Relationships
    source = relationship(Source, uselist=False)
    reference = relationship(Reference, uselist=False)
    locus = relationship(Locus, uselist=False, backref=backref('reservednames'))
    colleague = relationship(Colleague, uselist=False, backref=backref('reservednames', uselist=False))

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description',
                     'bud_id', 'reservation_date', 'expiration_date',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'locus', 'reference', 'colleague']
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['locus_id', 'colleague_id']


