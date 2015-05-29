from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.taxonomy import Taxonomy
from src.sgd.model.curate.reference import Reference
from src.sgd.model.curate.locus import Locus

__author__ = 'kelley'


class Posttranslationalannotation(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'posttranslationalannotation'

    id = Column('annotation_id', Integer, primary_key=True)
    dbentity_id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    taxonomy_id = Column('taxonomy_id', Integer, ForeignKey(Taxonomy.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    posttrans_type = Column('posttrans_type', String)
    site_index = Column('site_index', Integer)
    site_residue = Column('site_residue', String)
    site_functions = Column('site_functions', String)
    modifier_id = Column('modifier_id', Integer, ForeignKey(Locus.id))

    #Relationships
    dbentity = relationship(Dbentity, uselist=False, backref='posttranslational_annotations', foreign_keys=[dbentity_id])
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False)
    reference = relationship(Reference, uselist=False, foreign_keys=[reference_id])
    modifier = relationship(Locus, uselist=False, foreign_keys=[modifier_id])

    __eq_values__ = ['id', 'date_created', 'created_by', 'posttrans_type', 'site_index', 'site_residue', 'site_functions']
    __eq_fks__ = [('source', Source, False),
                  ('taxonomy', Taxonomy, False),
                  ('reference', Reference, False),
                  ('modifier', Locus, False),
                  ('dbentity', Dbentity, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['taxonomy_id', 'dbentity_id', 'reference_id', 'posttrans_type', 'site_residue', 'modifier_id']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    @classmethod
    def create_or_find(cls, obj_json, session):
        if obj_json is None:
            return None

        dbentity, dbentity_status = Dbentity.create_or_find(obj_json['dbentity'], session)

        if 'reference' in obj_json:
            reference, reference_status = Reference.create_or_find(obj_json['reference'], session)
            if reference_status != 'Found':
                raise Exception('Reference not found: ' + str(obj_json['reference']))

        if dbentity_status != 'Found':
            raise Exception('Dbentity not found: ' + str(obj_json['dbentity']))

        query = session.query(cls)\
            .filter_by(dbentity_id=dbentity.id)\
            .filter_by(posttrans_type=obj_json['posttrans_type'])\
            .filter_by(site_residue=obj_json['site_residue'])\
            .filter_by(site_index=obj_json['site_index'])\

        if 'reference' in obj_json:
            query = query.filter_by(reference_id=reference.id)

        current_obj = query.first()

        if current_obj is None:
            return cls(obj_json, session), 'Created'
        else:
            return current_obj, 'Found'

    def to_min_json(self, include_description=False):
        return self.to_json()
    def to_semi_json(self):
        return self.to_json()
