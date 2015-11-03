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
from src.sgd.model.nex.locus import Locus
from src.sgd.model.nex.psimod import Psimod

__author__ = 'sweng66'

class Posttranslationannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'posttranslationannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))
    site_index = Column('site_index', Integer)
    site_residue = Column('site_residue', String)
    psimod_id = Column('psimod_id', Integer, ForeignKey(Psimod.id))
    modifier_id = Column('modifier_id', Integer, ForeignKey(Locus.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    dbentity = relationship(Dbentity, uselist=False, foreign_keys=[dbentity_id])
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    modifier = relationship(Locus, uselist=False, foreign_keys=[modifier_id])
    psimod = relationship(Psimod, uselist=False)
    
    __eq_values__ = ['id', 'dbentity_id', 'taxonomy_id', 'reference_id', 'site_index', 'site_residue', 
                     'psimod_id', 'modifier_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('dbentity', Dbentity, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False),
                  ('modifier', Locus, False)]
                  
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_id', 'reference_id', 'psimod_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['dbentity'] = self.dbentity.display_name
        obj_json['reference'] = self.phenotype.citation
        obj_json['psimod'] = self.psimod.display_name
        obj_json['site_index'] = self.site_index
        obj_json['site_residue'] = self.site_residue
        return obj_json

