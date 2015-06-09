from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.reference import Reference
from src.sgd.model.curate.source import Source

__author__ = 'kelley'

class Locus(Dbentity):
    __tablename__ = "locusdbentity"

    id = Column('dbentity_id', String, ForeignKey(Dbentity.id), primary_key=True)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    locus_type = Column('locus_type', String)
    systematic_name = Column('systematic_name', String)
    gene_name = Column('gene_name', String)
    qualifier = Column('qualifier', String)
    genetic_position = Column('genetic_position', String)

    has_summary = Column('has_summary', Boolean)
    has_sequence = Column('has_sequence', Boolean)
    has_history = Column('has_history', Boolean)
    has_literature = Column('has_literature', Boolean)
    has_go = Column('has_go', Boolean)
    has_phenotype = Column('has_phenotype', Boolean)
    has_interaction = Column('has_interaction', Boolean)
    has_expression = Column('has_expression', Boolean)
    has_regulation = Column('has_regulation', Boolean)
    has_protein = Column('has_protein', Boolean)
    has_sequence_section = Column('has_sequence_section', Boolean)

    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Dbentity.id}

    __eq_values__ = ['id', 'name', 'link', 'description',
                     'bud_id', 'sgdid', 'dbentity_status', 'date_created', 'created_by',
                     'systematic_name',
                     'name_description', 'headline', 'locus_type', 'gene_name', 'qualifier', 'genetic_position',
                     'has_summary', 'has_history', 'has_literature', 'has_go', 'has_phenotype', 'has_interaction',
                     'has_expression', 'has_regulation', 'has_protein', 'has_sequence', 'has_sequence_section']
    __eq_fks__ = [('source', Source, False),
                  ('aliases', 'locus.LocusAlias', True),
                  ('urls', 'locus.LocusUrl', True),
                  ('documents', 'locus.LocusDocument', True),
                  ('children', 'locus.LocusRelation', False)]
    __id_values__ = ['sgdid', 'id', 'gene_name', 'systematic_name']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = ['locus_type', 'qualifier']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

        tabs = tab_information(self.dbentity_status, self.locus_type)
        for tab in tabs:
            setattr(self, tab, tabs[tab])

    @classmethod
    def __create_name__(cls, obj_json):
        return obj_json['systematic_name'] if 'gene_name' not in obj_json else obj_json['gene_name']

    def __to_medium_json__(self):
        obj_json = ToJsonMixin.__to_medium_json__()
        obj_json['locus_type'] = self.locus_type
        return obj_json

    def __to_(self):
        obj_json = ToJsonMixin.to_json(self)
        obj_json['parents'] = [x.to_json(perspective='child') for x in self.parents]

        # for key in ['summary_tab', 'history_tab', 'literature_tab', 'go_tab', 'phenotype_tab', 'interaction_tab',
        #              'expression_tab', 'regulation_tab', 'protein_tab', 'sequence_tab', 'wiki_tab', 'sequence_section']:
        #     obj_json[key] = getattr(self, key) == 1
        #
        # #Phenotype overview
        # classical_groups = dict()
        # large_scale_groups = dict()
        # strain_groups = dict()
        # for evidence in self.phenotype_evidences:
        #     if evidence.experiment.category == 'classical genetics':
        #         if evidence.mutant_type in classical_groups:
        #             if evidence.phenotype_id not in classical_groups[evidence.mutant_type]:
        #                 classical_groups[evidence.mutant_type][evidence.phenotype_id] = evidence.phenotype
        #         else:
        #             classical_groups[evidence.mutant_type] = {evidence.phenotype_id: evidence.phenotype}
        #     elif evidence.experiment.category == 'large-scale survey':
        #         if evidence.mutant_type in large_scale_groups:
        #             if evidence.phenotype_id not in large_scale_groups[evidence.mutant_type]:
        #                 large_scale_groups[evidence.mutant_type][evidence.phenotype_id] = evidence.phenotype
        #         else:
        #             large_scale_groups[evidence.mutant_type] = {evidence.phenotype_id: evidence.phenotype}
        #
        #     if evidence.strain is not None:
        #         if evidence.strain.display_name in strain_groups:
        #             strain_groups[evidence.strain.display_name] += 1
        #         else:
        #             strain_groups[evidence.strain.display_name] = 1
        # experiment_categories = []
        # mutant_types = set(classical_groups.keys())
        # mutant_types.update(large_scale_groups.keys())
        # for mutant_type in mutant_types:
        #     experiment_categories.append([mutant_type, 0 if mutant_type not in classical_groups else len(classical_groups[mutant_type]), 0 if mutant_type not in large_scale_groups else len(large_scale_groups[mutant_type])])
        # strains = []
        # for strain, count in strain_groups.iteritems():
        #     strains.append([strain, count])
        # experiment_categories.sort(key=lambda x: x[1] + x[2], reverse=True)
        # experiment_categories.insert(0, ['Mutant Type', 'classical genetics', 'large-scale survey'])
        # strains.sort(key=lambda x: x[1], reverse=True)
        # strains.insert(0, ['Strain', 'Annotations'])
        # obj_json['phenotype_overview'] = {'experiment_categories': experiment_categories,
        #                                   'strains': strains,
        #                                   'classical_phenotypes': dict([(x, [phenotype.to_min_json() for phenotype in y.values()]) for x, y in classical_groups.iteritems()]),
        #                                   'large_scale_phenotypes': dict([(x, [phenotype.to_min_json() for phenotype in y.values()]) for x, y in large_scale_groups.iteritems()])
        #                                   }
        #
        # #Go overview
        # go_date_paragraphs = [x.to_json() for x in self.paragraphs if x.category == 'GODATE']
        # go_paragraphs = [x.to_json() for x in self.paragraphs if x.category == 'GO']
        # manual_mf_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'molecular function' and x.annotation_type == 'manually curated'])
        # htp_mf_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'molecular function' and x.annotation_type == 'high-throughput'])
        # manual_bp_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'biological process' and x.annotation_type == 'manually curated'])
        # htp_bp_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'biological process' and x.annotation_type == 'high-throughput'])
        # manual_cc_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'cellular component' and x.annotation_type == 'manually curated'])
        # htp_cc_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'cellular component' and x.annotation_type == 'high-throughput'])
        # term_to_evidence_codes_qualifiers = dict([(x, (set(), set())) for x in manual_mf_terms.keys()])
        # term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in htp_mf_terms.keys()])
        # term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in manual_bp_terms.keys()])
        # term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in htp_bp_terms.keys()])
        # term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in manual_cc_terms.keys()])
        # term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in htp_cc_terms.keys()])
        # for evidence in self.go_evidences:
        #     if evidence.annotation_type != 'computational':
        #         if evidence.experiment_id is not None:
        #             term_to_evidence_codes_qualifiers[evidence.go_id][0].add(evidence.experiment)
        #         if evidence.qualifier is not None:
        #             term_to_evidence_codes_qualifiers[evidence.go_id][1].add(evidence.qualifier)
        #
        # obj_json['go_overview'] = {'paragraph': None if len(go_paragraphs) == 0 else go_paragraphs[0]['text'],
        #                            'go_slim': sorted(dict([(x.id, x.to_min_json()) for x in chain(*[[x.parent for x in y.go.parents if x.relation_type == 'GO_SLIM'] for y in self.go_evidences])]).values(), key=lambda x: x['display_name'].lower()),
        #                            'date_last_reviewed': None if len(go_date_paragraphs) == 0 else go_date_paragraphs[0]['text'],
        #                            'computational_annotation_count': len([x for x in self.go_evidences if x.annotation_type == 'computational']),
        #                            'manual_molecular_function_terms': sorted([dict({'term': x.to_min_json(),
        #                                                                             'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
        #                                                                             'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1]),
        #                                                                             }) for x in manual_mf_terms.values()], key=lambda x: x['term']['display_name'].lower()),
        #                            'manual_biological_process_terms': sorted([dict({'term': x.to_min_json(),
        #                                                                             'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
        #                                                                             'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
        #                                                                             }) for x in manual_bp_terms.values()], key=lambda x: x['term']['display_name'].lower()),
        #                            'manual_cellular_component_terms': sorted([dict({'term': x.to_min_json(),
        #                                                                             'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
        #                                                                             'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
        #                                                                             }) for x in manual_cc_terms.values()], key=lambda x: x['term']['display_name'].lower()),
        #                            'htp_molecular_function_terms': sorted([dict({'term': x.to_min_json(),
        #                                                                          'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
        #                                                                          'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
        #                                                                             }) for x in htp_mf_terms.values()], key=lambda x: x['term']['display_name'].lower()),
        #                            'htp_biological_process_terms': sorted([dict({'term': x.to_min_json(),
        #                                                                          'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
        #                                                                          'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
        #                                                                             }) for x in htp_bp_terms.values()], key=lambda x: x['term']['display_name'].lower()),
        #                            'htp_cellular_component_terms': sorted([dict({'term': x.to_min_json(),
        #                                                                          'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
        #                                                                          'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
        #                                                                             }) for x in htp_cc_terms.values()], key=lambda x: x['term']['display_name'].lower())}
        #
        # #Interaction
        # genetic_interactions = set()
        # physical_interactions = set()
        # genetic_interactions.update(self.geninteraction_evidences1)
        # genetic_interactions.update(self.geninteraction_evidences2)
        # physical_interactions.update(self.physinteraction_evidences1)
        # physical_interactions.update(self.physinteraction_evidences2)
        #
        # genetic_bioentities = set([x.locus2_id if x.locus1_id == self.id else x.locus1_id for x in genetic_interactions])
        # physical_bioentities = set([x.locus2_id if x.locus1_id == self.id else x.locus1_id for x in physical_interactions])
        #
        # A = len(genetic_bioentities)
        # B = len(physical_bioentities)
        # C = len(genetic_bioentities & physical_bioentities)
        # r, s, x = calc_venn_measurements(A, B, C)
        #
        # physical_experiments = dict()
        # genetic_experiments = dict()
        # experiment_id_to_name = dict()
        #
        # for genevidence in genetic_interactions:
        #     experiment_id = genevidence.experiment_id
        #     if experiment_id not in experiment_id_to_name:
        #         experiment_id_to_name[experiment_id] = genevidence.experiment.display_name
        #     experiment_name = experiment_id_to_name[experiment_id]
        #
        #     if experiment_name not in genetic_experiments:
        #         genetic_experiments[experiment_name] = 1
        #     else:
        #         genetic_experiments[experiment_name] += 1
        #
        # for physevidence in physical_interactions:
        #     experiment_id = physevidence.experiment_id
        #     if experiment_id not in experiment_id_to_name:
        #         experiment_id_to_name[experiment_id] = physevidence.experiment.display_name
        #     experiment_name = experiment_id_to_name[experiment_id]
        #
        #     if experiment_name not in physical_experiments:
        #         physical_experiments[experiment_name] = 1
        #     else:
        #         physical_experiments[experiment_name] += 1
        #
        # obj_json['interaction_overview'] = {'gen_circle_size': r, 'phys_circle_size':s, 'circle_distance': x,
        #                                     'num_gen_interactors': A, 'num_phys_interactors': B, 'num_both_interactors': C,
        #                                     'total_interactions': len(genetic_interactions) + len(physical_interactions),
        #                                     'total_interactors': len(genetic_bioentities | physical_bioentities),
        #                                     'physical_experiments': physical_experiments,
        #                                     'genetic_experiments': genetic_experiments
        #                                     }
        # #Regulation
        # regulation_paragraphs = [x.to_json(linkit=True) for x in self.paragraphs if x.category == 'REGULATION']
        #
        # obj_json['regulation_overview'] = {'target_count': len(set([x.locus2_id for x in self.regulation_evidences_targets])),
        #                                     'regulator_count':len(set([x.locus1_id for x in self.regulation_evidences_regulators])),
        #                                     'paragraph': None if len(regulation_paragraphs) == 0 else regulation_paragraphs[0]}
        #
        # #Literature
        # reference_ids = set([x.reference_id for x in self.literature_evidences])
        # reference_ids.update([x.reference_id for x in self.geninteraction_evidences1])
        # reference_ids.update([x.reference_id for x in self.geninteraction_evidences2])
        # reference_ids.update([x.reference_id for x in self.physinteraction_evidences1])
        # reference_ids.update([x.reference_id for x in self.physinteraction_evidences2])
        # reference_ids.update([x.reference_id for x in self.regulation_evidences_targets])
        # reference_ids.update([x.reference_id for x in self.regulation_evidences_regulators])
        # obj_json['literature_overview'] = {'total_count': len(reference_ids),
        #                                    'primary_count': len(set([x.reference_id for x in self.literature_evidences if x.topic == 'Primary Literature'])),
        #                                    'additional_count': len(set([x.reference_id for x in self.literature_evidences if x.topic == 'Additional Literature'])),
        #                                    'review_count': len(set([x.reference_id for x in self.literature_evidences if x.topic == 'Reviews']))}
        #
        # #Sequence
        # obj_json['sequence_overview'] = sorted(dict([(x.strain.id, x.strain.to_min_json()) for x in self.dnasequence_evidences]).values(), key=lambda x: x['display_name'])
        #
        # reference_protein_sequence = None
        # for protein_sequence in self.proteinsequence_evidences:
        #     if protein_sequence.strain_id == 1:
        #         reference_protein_sequence = protein_sequence
        # #Protein
        # obj_json['protein_overview'] = {
        #     'length': None if reference_protein_sequence is None else len(reference_protein_sequence.residues)-1,
        #     'molecular_weight': None if reference_protein_sequence is None else reference_protein_sequence.molecular_weight,
        #     'pi': None if reference_protein_sequence is None else reference_protein_sequence.pi
        # }
        #
        # #History
        # note_to_evidences = dict()
        # for historyevidence in self.history_evidences:
        #     if historyevidence.note in note_to_evidences:
        #         note_to_evidences[historyevidence.note].append(historyevidence)
        #     else:
        #         note_to_evidences[historyevidence.note] = [historyevidence]
        #
        # historyevidences = []
        # for note, evidences in note_to_evidences.iteritems():
        #     evidence_json = evidences[0].to_json()
        #     del evidence_json['reference']
        #     evidence_json['references'] = [x.reference.to_min_json() for x in sorted(evidences, key=lambda y:None if y.reference is None else y.reference.year) if x.reference_id is not None]
        #     historyevidences.append(evidence_json)
        #
        #
        # obj_json['history'] = historyevidences
        #
        # obj_json['paralogs'] = [x.to_json() for x in self.children if x.relation_type == 'paralog']
        #
        # obj_json['qualities'] = dict([(x.display_name.lower().replace(' ', '_'), x.to_json()) for x in self.qualities])
        #
        # ordered_references = self.get_ordered_references()
        # obj_json['references'] = [x.to_semi_json() for x in ordered_references]
        # reference_mapping = {}
        # for reference in ordered_references:
        #     reference_mapping[reference.id] = len(reference_mapping)+1
        #
        # obj_json['reference_mapping'] = reference_mapping
        #
        # if self.reserved_name is not None:
        #     obj_json['reserved_name'] = self.reserved_name.to_json()
        #
        # obj_json['pathways'] = [x.to_json() for x in self.pathway_evidences]
        #
        # obj_json['ecnumbers'] = None if len(self.ecnumber_evidences) == 0 else [x.ecnumber.to_min_json() for x in self.ecnumber_evidences]

        return obj_json

class LocusUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locus_url'

    id = Column('url_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    locus_id = Column('locus_id', String, ForeignKey(Locus.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    placement = Column('placement', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    locus = relationship(Locus, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'url_type', 'placement',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.locus is None else self.locus.unique_key()), self.name, self.placement, self.url_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.locus_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(locus_id=newly_created_object.locus_id)\
            .filter_by(name=newly_created_object.name)\
            .filter_by(url_type=newly_created_object.url_type)\
            .filter_by(placement=newly_created_object.placement).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'name': self.name,
            'link': self.link,
            'source': self.source.to_json(size='small'),
            'url_type': self.url_type,
            'placement': self.placement
        }


class LocusAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locus_alias'

    id = Column('alias_id', Integer, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    locus_id = Column('locus_id', String, ForeignKey(Locus.id, ondelete='CASCADE'))
    is_external_id = Column('is_external_id', Integer)
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    locus = relationship(Locus, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'name', 'link', 'bud_id', 'is_external_id', 'alias_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)
        self.is_external_id = 0 if self.alias_type in {'Uniform', 'Non-uniform', 'NCBI protein name', 'Retired name'} else 1

    def unique_key(self):
        return (None if self.locus is None else self.locus.unique_key()), self.name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.locus_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(locus_id=newly_created_object.locus_id)\
            .filter_by(name=newly_created_object.name)\
            .filter_by(alias_type=newly_created_object.alias_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'name': self.name,
            'link': self.link,
            'source': self.source.to_json(size='small'),
            'alias_type': self.alias_type
        }


class LocusDocument(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locus_document'

    id = Column('document_id', Integer, primary_key=True)
    document_type = Column('document_type', String)
    document_order = Column('document_order', Integer, default=1)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    locus_id = Column('locus_id', String, ForeignKey(Locus.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    locus = relationship(Locus, uselist=False, backref=backref('documents', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'document_type', 'document_order',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('references', 'locus.LocusDocumentReference', False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.locus is None else self.locus.unique_key()), self.document_type, self.document_order

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        current_obj = session.query(cls)\
            .filter_by(locus_id=parent_obj.id)\
            .filter_by(document_type=obj_json['document_type'])\
            .filter_by(document_order=1 if 'document_order' not in obj_json else obj_json['document_order']).first()

        if current_obj is None:
            return cls(obj_json, session), 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        return {
            'text': self.html,
            'source': self.source.to_json(size='small'),
            'document_type': self.document_type,
            'document_order': self.document_order,
            'references': [x.to_json(size='small') for x in self.references]
        }


class LocusDocumentReference(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locus_document_reference'

    id = Column('document_reference_id', Integer, primary_key=True)
    document_id = Column('document_id', String, ForeignKey(LocusDocument.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', String, ForeignKey(Reference.id, ondelete='CASCADE'))
    reference_order = Column('reference_order', Integer)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    document = relationship(LocusDocument, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    reference = relationship(Reference, uselist=False, backref=backref('locus_documents', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'reference_order', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, document, reference, reference_order):
        self.reference_order = reference_order
        self.document = document
        self.reference_id = reference.id
        self.source = self.document.source

    def unique_key(self):
        return (None if self.document is None else self.document.unique_key()), (self.reference_id if self.reference is None else self.reference.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        reference, status = Reference.create_or_find(obj_json, session)
        if status == 'Created':
            raise Exception('Reference not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(document_id=parent_obj.id)\
            .filter_by(reference_id=reference.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, reference, obj_json['reference_order'])
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self, size='small'):
        if self.reference is None:
            return None
        obj_json = self.reference.to_json(size='medium')
        obj_json['reference_order'] = self.reference_order
        return obj_json


class LocusRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'locus_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', String, ForeignKey(Source.id))
    parent_id = Column('parent_id', String, ForeignKey(Locus.id, ondelete='CASCADE'))
    child_id = Column('child_id', String, ForeignKey(Locus.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Locus, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Locus, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('parent', Locus, False),
                  ('child', Locus, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, parent, child, relation_type):
        self.parent = parent
        self.child = child
        self.source = self.child.source
        self.relation_type = relation_type

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key(), self.relation_type)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Locus.create_or_find(obj_json, session)
        if status == 'Created':
            raise Exception('Child locus not found: ' + str(obj_json))

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

    def to_json(self, size='small', perspective='parent'):
        if perspective == 'parent':
            obj_json = self.child.to_json(size='small')
        elif perspective == 'child':
            obj_json = self.parent.to_json(size='small')

        if obj_json is not None:
            obj_json['relation_type'] = self.relation_type
        return obj_json


#def create_i(reference, reference_index, extra_text):
#    new_i = '<span data-tooltip aria-haspopup="true" class="has-tip" title="' + extra_text + (' ' if len(extra_text) > 0 else '') + reference.display_name + '"><a href="#reference"><sup>' + str(reference_index) + '</sup></a></span>'
#    return new_ir


def tab_information(status, locus_type):
    if status == 'Merged' or status == 'Deleted':
        return {
            'has_summary': 1,
            'has_sequence': 0,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 0,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    elif locus_type == 'ORF' or locus_type == 'blocked_reading_frame':
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 1,
            'has_regulation': 1,
            'has_protein': 1,
        }
    elif locus_type in {'ARS', 'origin_of_replication', 'matrix_attachment_site', 'centromere',
                              'gene_group', 'long_terminal_repeat', 'telomere', 'mating_type_region',
                              'silent_mating_type_cassette_array', 'LTR_retrotransposon'}:
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    elif locus_type == 'transposable_element_gene':
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 1,
        }
    elif locus_type == 'pseudogene':
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 1,
            'has_protein': 1,
        }
    elif locus_type in {'rRNA_gene', 'ncRNA_gene', 'snRNA_gene', 'snoRNA_gene', 'tRNA_gene', 'telomerase_RNA_gene'}:
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 1,
            'has_protein': 0,
        }
    elif locus_type in {'not in systematic sequence of S288C', 'not physically mapped'}:
        return {
            'has_summary': 1,
            'has_sequence': 0,
            'has_sequence_section': 0,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    elif locus_type in {'intein_encoding_region'}:
        return {
            'has_summary': 1,
            'has_sequence': 0,
            'has_sequence_section': 0,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    else:
        raise Exception('Locus type is invalid.')