from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.reference import Reference
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.colleague import Colleague
from src.sgd.model.curate.taxonomy import Taxonomy

__author__ = 'kkarra'


class Historyannotation(Base, EqualityByIDMixin):
    __tablename__ = 'historyannotation'

    id = Column('annotation_id', String, primary_key=True)
    dbentity_id = Column('dbentity_id', String, ForeignKey(Dbentity.id))
    source_id = Column('source_id', ForeignKey(Source.id))
    reference_id = Column('reference_id', String)
    taxonomy_id = Column('taxonomy_id', String, ForeignKey(Taxonomy.id))
    bud_id = Column('bud_id', Integer)
    colleague_id = Column('colleague_id',String, ForeignKey(Colleague.id))
    date_annotation_made = Column('date_annotation_made', Date, server_default=FetchedValue())
    subclass = Column('subclass', String)
    history_type = Column('history_type', String)
    history_note = Column('history_note', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    source = relationship(Source, uselist=False)
    #reference = relationship(Reference, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, backref=backref('historyannotations', uselist=False))
    colleague = relationship(Colleague, uselist=False, backref=backref('historyannotations', uselist=False))

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'created_by', 'date_created']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['name', 'id']
    __no_edit_values__ = ['id', 'name', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_id', 'colleague_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)
