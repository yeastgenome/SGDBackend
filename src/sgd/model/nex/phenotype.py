from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.curate.qualifier import Qualifier
from src.sgd.model.curate.observable import Observable
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Phenotype(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'phenotype'

    id = Column('phenotype_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    observable_id = Column('observable_id', ForeignKey(Observable.id))
    qualifier_id = Column('qualifier_id', ForeignKey(Qualifier.id))
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    observable = relationship(Observable, uselist=False)
    qualifier = relationship(Qualifier, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('observable', Observable, False),
                  ('qualifier', Qualifier, False)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['observable_id', 'qualifier_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return create_format_name(('' if 'qualifier' not in obj_json else obj_json['qualifier']['display_name'] + '.') + obj_json['observable']['display_name'])[:100]

    @classmethod
    def __create_display_name__(cls, obj_json):
        return (obj_json['observable']['display_name'] + ('' if 'qualifier' not in obj_json else ': ' + obj_json['qualifier']['display_name']))[:500]

    @hybrid_property
    def evidences(self):
        return self.phenotype_evidences

    # def to_json(self):
    #     obj_json = UpdateWithJsonMixin.to_json(self)
    #
    #     #Phenotype overview
    #     classical_groups = dict()
    #     large_scale_groups = dict()
    #     strain_groups = dict()
    #     for evidence in self.phenotype_evidences:
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
    #     return obj_json

