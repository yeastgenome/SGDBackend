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

    __eq_values__ = ['id', 'annotation_type', 'bud_id', 'dbentity_id', 'taxonomy_id', 
                     'reference_id', 'go_id', 'eco_id', 'go_qualifier', 'date_assigned', 
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('dbentity', Dbentity, False),
                  ('reference', Reference, False),
                  ('taxonomy', Taxonomy, False),
                  ('go', Go, False),
                  ('eco', Eco, False),
                  ('goextensions', 'goannotation.Goextension', True),
                  ('gosupportingevidences', 'goannotation.Gosupportingevidence', True)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = ['dbentity_id', 'reference_id', 'go_id']

    def __init__(self, obj_json, session):
        self.dbentity_id = obj_json['dbentity_id']
        self.reference_id = obj_json['reference_id']
        self.taxonomy_id = obj_json['taxonomy_id']
        self.go_id = obj_json['go_id']
        self.eco_id = obj_json['eco_id']
        self.go_qualifier = obj_json['go_qualifier']
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __to_small_json__(self):
        obj_json = ToJsonMixin.__to_small_json__(self)
        obj_json['dbentity'] = self.dbentity.display_name
        obj_json['reference'] = self.phenotype.citation
        obj_json['go'] = self.go.display_name
        obj_json['annotation_type'] = self.annotation_type
        return obj_json

    def __to_large_json__(self):
        obj_json = ToJsonMixin.__to_large_json__(self)
        obj_json['dbentity'] = self.dbentity.display_name
        obj_json['reference'] = self.phenotype.citation
        obj_json['go'] = self.go.display_name
        obj_json['annotation_type'] = self.annotation_type
        obj_json['eco'] = self.eco.display_name
        obj_json['date_assigned'] = self.date_assigned
        return obj_json

 
class Goextension(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'goextension'

    id = Column('goextension_id', Integer, primary_key=True)
    annotation_id = Column('annotation_id', Integer, ForeignKey(Goannotation.id, ondelete='CASCADE'))
    link = Column('obj_url', String)
    group_id = Column('group_id', Integer)
    dbxref_id = Column('dbxref_id', String)
    ro_id = Column('ro_id', Integer, ForeignKey(Ro.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships                                                                                                                           
    annotation = relationship(Goannotation, uselist=False, backref=backref('goextensions', cascade="all, delete-orphan", passive_deletes=True))
    ro = relationship('Ro')
    role = association_proxy('ro', 'display_name')

    __eq_values__ = ['id', 'link', 'group_id', 'ro_id', 'dbxref_id']
    __eq_fks__ = []
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.group_id = obj_json['group_id']
        self.dbxref_id = obj_json['dbxref_id']
        self.link = obj_json['link']
        self.ro_id = obj_json['ro_id']
        print "GO_EXTENSION-obj_json: ", obj_json
        self.update(obj_json, session)

    def unique_key(self):
        return self.annotation_id, self.group_id, self.dbxref_id, self.link, self.ro_id

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None
        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.annotation_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(group_id=newly_created_object.group_id)\
            .filter_by(ro_id=newly_created_object.ro_id)\
            .filter_by(dbxref_id=newly_created_object.dbxref_id)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'group_id': self.group_id,
            'dbxref_id': self.dbxref_id,
            'link': self.link,
            'role': self.role
        }

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

    __eq_values__ = ['id', 'link', 'group_id', 'evidence_type', 'dbxref_id']
    __eq_fks__ = []
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        # print "GO_SUPPORT-obj_json: ", obj_json
        self.group_id = obj_json['group_id']
        self.dbxref_id = obj_json['dbxref_id']
        self.evidence_type = obj_json['evidence_type']
        self.link = obj_json['link']
        self.update(obj_json, session)

    def unique_key(self):
        return self.annotation_id, self.group_id, self.dbxref_id, self.link, self.evidence_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None
        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.annotation_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(group_id=newly_created_object.group_id)\
            .filter_by(evidence_type=newly_created_object.evidence_type)\
            .filter_by(dbxref_id=newly_created_object.dbxref_id)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'group_id': self.group_id,
            'dbxref_id': self.dbxref_id,
            'link': self.link,
            'evidence': self.evidence_type
        }
