from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.taxonomy import Taxonomy
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.pathway import Pathway
from src.sgd.model.nex.ec import Ec

__author__ = 'sweng66'

class Pathwayannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'pathwayannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    pathway_id = Column('pathway_id', Integer, ForeignKey(Pathway.id))
    ec_id = Column('ec_id', Integer, ForeignKey(Ec.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    pathway = relationship(Pathway, uselist=False, foreign_keys=[pathway_id])

    ec = relationship(Ec, uselist=False)
        
    __eq_values__ = ['id', 'ec_id', 'dbentity_id', 'pathway_id', 'bud_id', 'reference_id',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('dbentity', Dbentity, False),
                  ('pathway', Pathway, False),
                  ('reference', Reference, False),
                  ('ec', Ec, False),
                  ('taxonomy', Taxonomy, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_id', 'ec_id', 'reference_id', 'pathway_id']

    def __init__(self, obj_json, session):
        self.taxonomy_id = obj_json['taxonomy_id']
        UpdateWithJsonMixin.__init__(self, obj_json, session)



 

