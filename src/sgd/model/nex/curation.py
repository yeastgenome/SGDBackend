from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.locus import Locus

__author__ = 'sweng66'

class Curation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'curation'

    id = Column('curation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id))
    bud_id = Column('bud_id', Integer)
    subclass = Column('subclass', String)
    curation_task = Column('curation_task', String)
    curator_comment = Column('curator_comment', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    locus = relationship(Locus, uselist=False, foreign_keys=[locus_id])

    __eq_values__ = ['id', 'subclass', 'bud_id', 'dbentity_id', 'locus_id', 'curation_task', 
                     'curator_comment', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('dbentity', Dbentity, False),
                  ('locus', Locus, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_id', 'locus_id', 'curation_task']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)


