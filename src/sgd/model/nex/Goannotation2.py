from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.go import Go
from src.sgd.model.nex.eco import Eco
from src.sgd.model.nex.ro import Ro
from src.sgd.model.nex.goextension2 import Goextension
from src.sgd.model.nex.gosupportingevidence2 import Gosupportingevidence

__author__ = 'sweng66'

class Goannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'goannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    eco_id = Column('eco_id', Integer, ForeignKey(Eco.id))
    annotation_type = Column('annotation_type', String)
    go_qualifier = Column('go_qualifier', String)
    date_assigned = Column('date_assigned', Date, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    go = relationship(Go, uselist=False)
    eco = relationship(Eco, uselist=False)
    # goextensions = relationship(Goextension, uselist=False, foreign_keys=[annotation_id])
    # gosupportingevidences = relationship(Gosupportingevidence, uselist=False, foreign_keys=[annotation_id])

    __eq_values__ = ['id', 'annotation_type', 'bud_id', 'dbentity_id', 'taxonomy_id', 
                     'reference_id', 'go_id', 'eco_id', 'go_qualifier', 'date_assigned', 
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('dbentity', Dbentity, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False),
                  ('go', Go, False),
                  ('eco', Eco, False)]
                  # ('goextensions', Goextension, False),
                  # ('gosupportingevidences', Gosupportingevidence, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_id', 'reference_id', 'go_id', 'annotation_type']

    def __init__(self, dbentity_id, source_id, taxonomy_id, reference_id, go_id, eco_id, annotation_type, go_qualifier, date_assigned, date_created, created_by):
        self.dbentity_id = dbentity_id
        self.source_id = source_id
        self.taxonomy_id = taxonomy_id
        self.reference_id = reference_id
        self.go_id = go_id
        self.eco_id = eco_id
        self.annotation_type = annotation_type
        self.go_qualifier = go_qualifier
        self.date_assigned = date_assigned
        self.date_created = date_created
        self.created_by = created_by




