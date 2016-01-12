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
from src.sgd.model.nex.psimod import Psimod

__author__ = 'sweng66'

class Physinteractionannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'physinteractionannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity1_id = Column('dbentity1_id', Integer, ForeignKey(Dbentity.id))
    dbentity2_id = Column('dbentity2_id', Integer, ForeignKey(Dbentity.id))  
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    psimod_id = Column('psimod_id', Integer, ForeignKey(Psimod.id))
    biogrid_experimental_system = Column('biogrid_experimental_system', String)
    annotation_type = Column('annotation_type', String)
    bait_hit = Column('bait_hit', String) 
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    dbentity1 = relationship(Dbentity, uselist=False, foreign_keys=[dbentity1_id])
    dbentity2 = relationship(Dbentity, uselist=False, foreign_keys=[dbentity2_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    psimod = relationship(Psimod, uselist=False)

    __eq_values__ = ['id', 'dbentity1_id', 'dbentity1_id', 'bud_id',
                     'taxonomy_id', 'reference_id', 'psimod_id', 
                     'biogrid_experimental_system', 'annotation_type', 
                     'bait_hit', 'description', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('dbentity1', Dbentity, False),
                  ('dbentity2', Dbentity, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False),
                  ('psimod', Psimod, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity1_id', 'dbentity2_id', 'reference_id', 'psimod_id', 'annotation_type']

    def __init__(self, obj_json, session):
        self.dbentity1_id = obj_json['dbentity1_id']
        self.dbentity2_id = obj_json['dbentity2_id']
        self.reference_id = obj_json['reference_id']
        self.taxonomy_id = obj_json['taxonomy_id']
        self.psimod_id = obj_json.get('psimod_id')
        self.biogrid_experimental_system = obj_json['biogrid_experimental_system']
        self.annotation_type = obj_json['annotation_type']
        self.bait_hit = obj_json['bait_hit']
        self.description = obj_json.get('description')
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['dbentity1'] = self.dbentity1.display_name
        obj_json['dbentity2'] = self.dbentity2.display_name
        obj_json['reference'] = self.reference.citation
        obj_json['psimod'] = self.psimod.display_name
        obj_json['annotation_type'] = self.annotation_type
        obj_json['bait_hit'] = self.bait_hit
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['dbentity1'] = self.dbentity1.display_name
        obj_json['dbentity2'] = self.dbentity2.display_name
        obj_json['reference'] = self.reference.citation
        obj_json['psimod'] = self.psimod.display_name
        obj_json['annotation_type'] = self.annotation_type
        obj_json['bait_hit'] = self.bait_hit
        obj_json['description'] = self.description
        obj_json['biogrid_experimental_system'] = self.biogrid_experimental_system
        return obj_json

