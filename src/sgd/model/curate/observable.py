from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Observable(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'observable'

    id = Column('observable_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    apo_id = Column('apo_id', String)
    observable_type = Column('observable_type', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'bud_id', 'date_created', 'created_by',
                     'apo_id', 'observable_type']
    __eq_fks__ = [('source', Source, False),
                  ('aliases', 'observable.ObservableAlias', True),
                  ('children', 'observable.ObservableRelation', True)]
    __id_values__ = ['id', 'display_name', 'format_name', 'apo_id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['observable_type']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return create_format_name(obj_json['display_name'])[:100] if 'apo_id' not in obj_json else obj_json['apo_id']

    @hybrid_property
    def evidences(self):
        return set(sum([x.phenotype_evidences for x in self.phenotypes], []))

    @hybrid_property
    def is_root(self):
        return self.format_name == 'ypo'

    # def to_json(self):
    #     obj_json = UpdateWithJsonMixin.to_json(self)
    #
    #     #Phenotype overview
    #     phenotype_evidences = []
    #     for phenotype in self.phenotypes:
    #         phenotype_evidences.extend(phenotype.phenotype_evidences)
    #
    #     classical_groups = dict()
    #     large_scale_groups = dict()
    #     strain_groups = dict()
    #     for evidence in phenotype_evidences:
    #         if evidence.experiment.category == 'classical genetics':
    #             if evidence.mutant_type in classical_groups:
    #                 classical_groups[evidence.mutant_type] += 1
    #             else:
    #                 classical_groups[evidence.mutant_type] = 1
    #         elif evidence.experiment.category == 'large-scale survey':
    #             if evidence.mutant_type in large_scale_groups:
    #                 large_scale_groups[evidence.mutant_type] += 1
    #             else:
    #                 large_scale_groups[evidence.mutant_type] = 1
    #
    #         if evidence.strain is not None:
    #             if evidence.strain.display_name in strain_groups:
    #                 strain_groups[evidence.strain.display_name] += 1
    #             else:
    #                 strain_groups[evidence.strain.display_name] = 1
    #     experiment_categories = []
    #     mutant_types = set(classical_groups.keys())
    #     mutant_types.update(large_scale_groups.keys())
    #     for mutant_type in mutant_types:
    #         experiment_categories.append([mutant_type, 0 if mutant_type not in classical_groups else classical_groups[mutant_type], 0 if mutant_type not in large_scale_groups else large_scale_groups[mutant_type]])
    #
    #     strains = []
    #     for strain, count in strain_groups.iteritems():
    #         strains.append([strain, count])
    #     experiment_categories.sort(key=lambda x: x[1] + x[2], reverse=True)
    #     experiment_categories.insert(0, ['Mutant Type', 'classical genetics', 'large-scale survey'])
    #     strains.sort(key=lambda x: x[1], reverse=True)
    #     strains.insert(0, ['Strain', 'Annotations'])
    #     obj_json['overview'] = {'experiment_categories': experiment_categories,
    #                                       'strains': strains}
    #
    #     #Phenotypes
    #     obj_json['phenotypes'] = []
    #     for phenotype in self.phenotypes:
    #         phenotype_json = phenotype.to_min_json()
    #         phenotype_json['qualifier'] = phenotype.qualifier
    #         obj_json['phenotypes'].append(phenotype_json)
    #
    #     #Counts
    #     obj_json['locus_count'] = self.locus_count
    #     obj_json['descendant_locus_count'] = self.descendant_locus_count

        return obj_json


class ObservableAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'observable_alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    observable_id = Column('observable_id', Integer, ForeignKey(Observable.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    observable = relationship(Observable, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'alias_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.observable is None else self.observable.unique_key()), self.display_name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.observable_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(observable_id=newly_created_object.observable_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(alias_type=newly_created_object.alias_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ObservableRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'observable_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    parent_id = Column('parent_id', Integer, ForeignKey(Observable.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Observable.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Observable, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Observable, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('parent', Observable, False),
                  ('child', Observable, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, parent, child, relation_type):
        self.relation_type = relation_type
        self.source = child.source
        self.parent = parent
        self.child = child

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key(), self.relation_type)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Observable.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Child reference not found: ' + str(obj_json))

        relation_type = obj_json["relation_type"]

        current_obj = session.query(cls)\
            .filter_by(parent_id=parent_obj.id)\
            .filter_by(child_id=child.id)\
            .filter_by(relation_type=relation_type).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, child, relation_type)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self):
        obj_json = self.child.to_min_json()
        obj_json['source'] = self.child.source.to_min_json()
        obj_json['relation_type'] = self.relation_type