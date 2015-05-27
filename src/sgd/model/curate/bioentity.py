from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from bioconcept import Go
from src.sgd.model.nex.misc import Alias, Url, Relation, Quality, Source
from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin
from venn import calc_venn_measurements
from itertools import chain

__author__ = 'kpaskov'

class Bioentity(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'bioentity'
    
    id = Column('bioentity_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    sgdid = Column('sgdid', String)
    uniprotid = Column('uniprotid', String)
    bioent_status = Column('bioent_status', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    
    __mapper_args__ = {'polymorphic_on': class_type}
            
    def unique_key(self):
        return self.format_name, self.class_type
    
class Bioentityurl(Url):
    __tablename__ = 'bioentityurl'
    
    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Url.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioentity_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioentity_id'))

class Bioentityalias(Alias):
    __tablename__ = 'bioentityalias'
    
    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))
    is_external_id = Column('is_external_id', Integer)

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Alias.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioentity_id', 'is_external_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioentity_id'))

class Bioentityrelation(Relation):
    __tablename__ = 'bioentityrelation'

    id = Column('relation_id', Integer, ForeignKey(Relation.id), primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioentity.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    parent = relationship(Bioentity, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Bioentity, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    
    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))

class Bioentityquality(Quality):
    __tablename__ = 'bioentityquality'

    id = Column('quality_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioentity_id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id))

    #Relationships
    bioentity = relationship(Bioentity, uselist=False, backref=backref('qualities', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOENTITY', 'inherit_condition': id == Quality.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'value',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'bioentity']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioentity').id)

# class Locus(Bioentity):
#     __tablename__ = "locusbioentity"
#
#     id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
#     name_description = Column('name_description', String)
#     headline = Column('headline', String)
#     locus_type = Column('locus_type', String)
#     gene_name = Column('gene_name', String)
#     qualifier = Column('qualifier', String)
#     genetic_position = Column('genetic_position', Integer)
#
#     __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Bioentity.id}
#     __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
#                      'description',
#                      'name_description', 'headline', 'locus_type', 'gene_name', 'qualifier', 'genetic_position',
#                      'date_created', 'created_by']
#     __eq_fks__ = ['source']
#
#     def __init__(self, obj_json):
#         UpdateByJsonMixin.__init__(self, obj_json)
#         self.link = None if obj_json.get('sgdid') is None else '/locus/' + self.sgdid + '/overview'
#
#     def to_semi_json(self):
#         obj_json = UpdateByJsonMixin.to_min_json(self)
#         obj_json['description'] = self.description
#         return obj_json
#
#     def get_ordered_references(self):
#         references = []
#         reference_ids = set()
#
#         # Organize pre- quality references
#         pre_quality_order = {'Gene Name': 0, 'ID': 1, 'Feature Type': 2, 'Qualifier': 3}
#         for quality in sorted([x for x in self.qualities if x.display_name in pre_quality_order], key=lambda x: pre_quality_order[x.display_name]):
#             for quality_reference in sorted(quality.quality_references, key=lambda x: x.reference.year, reverse=True):
#                 if quality_reference.reference_id not in reference_ids:
#                     references.append(quality_reference.reference)
#                     reference_ids.add(quality_reference.reference_id)
#
#         #Organize alias references
#         for alias in self.aliases:
#             if alias.category == 'Alias':
#                 for alias_reference in sorted(alias.alias_references, key=lambda x: x.reference.year, reverse=True):
#                     if alias_reference.reference_id not in reference_ids:
#                         references.append(alias_reference.reference)
#                         reference_ids.add(alias_reference.reference_id)
#
#         # Organize post- quality references
#         post_quality_order = {'Description': 4, 'Name Description': 5, 'Headline': 6, 'Genetic Position': 7}
#         for quality in sorted([x for x in self.qualities if x.display_name not in pre_quality_order], key=lambda x: 10 if x.display_name not in post_quality_order else post_quality_order[x.display_name]):
#             for quality_reference in sorted(quality.quality_references, key=lambda x: x.reference.year, reverse=True):
#                 if quality_reference.reference_id not in reference_ids:
#                     references.append(quality_reference.reference)
#                     reference_ids.add(quality_reference.reference_id)
#
#         #Organize paralog references
#         paralogs = [x for x in self.children if x.relation_type == 'paralog']
#         if len(paralogs) > 0:
#             for paralog in paralogs:
#                 for relation_reference in sorted(paralog.relation_references, key=lambda x: x.reference.year, reverse=True):
#                     if relation_reference.reference_id not in reference_ids:
#                         references.append(relation_reference.reference)
#                         reference_ids.add(relation_reference.reference_id)
#
#         #Organize gene reservation references
#         if self.reserved_name is not None and self.reserved_name.reference is not None and self.reserved_name.reference_id not in reference_ids:
#             references.append(self.reserved_name.reference)
#             reference_ids.add(self.reserved_name.reference_id)
#
#         # Organize paragraph references
#         lsp_paragraphs = [x for x in self.paragraphs if x.category == 'LSP']
#         if len(lsp_paragraphs) > 0:
#             for paragraph_reference in lsp_paragraphs[0].paragraph_references:
#                 if paragraph_reference.reference_id not in reference_ids:
#                     references.append(paragraph_reference.reference)
#                     reference_ids.add(paragraph_reference.reference_id)
#
#         return references
#
#     def to_json(self):
#         obj_json = UpdateByJsonMixin.to_json(self)
#
#         #Phenotype overview
#         classical_groups = dict()
#         large_scale_groups = dict()
#         strain_groups = dict()
#         for evidence in self.phenotype_evidences:
#             if evidence.experiment.category == 'classical genetics':
#                 if evidence.mutant_type in classical_groups:
#                     if evidence.phenotype_id not in classical_groups[evidence.mutant_type]:
#                         classical_groups[evidence.mutant_type][evidence.phenotype_id] = evidence.phenotype
#                 else:
#                     classical_groups[evidence.mutant_type] = {evidence.phenotype_id: evidence.phenotype}
#             elif evidence.experiment.category == 'large-scale survey':
#                 if evidence.mutant_type in large_scale_groups:
#                     if evidence.phenotype_id not in large_scale_groups[evidence.mutant_type]:
#                         large_scale_groups[evidence.mutant_type][evidence.phenotype_id] = evidence.phenotype
#                 else:
#                     large_scale_groups[evidence.mutant_type] = {evidence.phenotype_id: evidence.phenotype}
#
#             if evidence.strain is not None:
#                 if evidence.strain.display_name in strain_groups:
#                     strain_groups[evidence.strain.display_name] += 1
#                 else:
#                     strain_groups[evidence.strain.display_name] = 1
#         experiment_categories = []
#         mutant_types = set(classical_groups.keys())
#         mutant_types.update(large_scale_groups.keys())
#         for mutant_type in mutant_types:
#             experiment_categories.append([mutant_type, 0 if mutant_type not in classical_groups else len(classical_groups[mutant_type]), 0 if mutant_type not in large_scale_groups else len(large_scale_groups[mutant_type])])
#         strains = []
#         for strain, count in strain_groups.iteritems():
#             strains.append([strain, count])
#         experiment_categories.sort(key=lambda x: x[1] + x[2], reverse=True)
#         experiment_categories.insert(0, ['Mutant Type', 'classical genetics', 'large-scale survey'])
#         strains.sort(key=lambda x: x[1], reverse=True)
#         strains.insert(0, ['Strain', 'Annotations'])
#         obj_json['phenotype_overview'] = {'experiment_categories': experiment_categories,
#                                           'strains': strains,
#                                           'classical_phenotypes': dict([(x, [phenotype.to_min_json() for phenotype in y.values()]) for x, y in classical_groups.iteritems()]),
#                                           'large_scale_phenotypes': dict([(x, [phenotype.to_min_json() for phenotype in y.values()]) for x, y in large_scale_groups.iteritems()])
#                                           }
#
#         #Go overview
#         go_date_paragraphs = [x.to_json() for x in self.paragraphs if x.category == 'GODATE']
#         go_paragraphs = [x.to_json() for x in self.paragraphs if x.category == 'GO']
#         manual_mf_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'molecular function' and x.annotation_type == 'manually curated'])
#         htp_mf_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'molecular function' and x.annotation_type == 'high-throughput'])
#         manual_bp_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'biological process' and x.annotation_type == 'manually curated'])
#         htp_bp_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'biological process' and x.annotation_type == 'high-throughput'])
#         manual_cc_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'cellular component' and x.annotation_type == 'manually curated'])
#         htp_cc_terms = dict([(x.go.id, x.go) for x in self.go_evidences if x.go.go_aspect == 'cellular component' and x.annotation_type == 'high-throughput'])
#         term_to_evidence_codes_qualifiers = dict([(x, (set(), set())) for x in manual_mf_terms.keys()])
#         term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in htp_mf_terms.keys()])
#         term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in manual_bp_terms.keys()])
#         term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in htp_bp_terms.keys()])
#         term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in manual_cc_terms.keys()])
#         term_to_evidence_codes_qualifiers.update([(x, (set(), set())) for x in htp_cc_terms.keys()])
#         for evidence in self.go_evidences:
#             if evidence.annotation_type != 'computational':
#                 if evidence.experiment_id is not None:
#                     term_to_evidence_codes_qualifiers[evidence.go_id][0].add(evidence.experiment)
#                 if evidence.qualifier is not None:
#                     term_to_evidence_codes_qualifiers[evidence.go_id][1].add(evidence.qualifier)
#
#         obj_json['go_overview'] = {'paragraph': None if len(go_paragraphs) == 0 else go_paragraphs[0]['text'],
#                                    'go_slim': sorted(dict([(x.id, x.to_min_json()) for x in chain(*[[x.parent for x in y.go.parents if x.relation_type == 'GO_SLIM'] for y in self.go_evidences])]).values(), key=lambda x: x['display_name'].lower()),
#                                    'date_last_reviewed': None if len(go_date_paragraphs) == 0 else go_date_paragraphs[0]['text'],
#                                    'computational_annotation_count': len([x for x in self.go_evidences if x.annotation_type == 'computational']),
#                                    'manual_molecular_function_terms': sorted([dict({'term': x.to_min_json(),
#                                                                                     'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
#                                                                                     'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1]),
#                                                                                     }) for x in manual_mf_terms.values()], key=lambda x: x['term']['display_name'].lower()),
#                                    'manual_biological_process_terms': sorted([dict({'term': x.to_min_json(),
#                                                                                     'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
#                                                                                     'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
#                                                                                     }) for x in manual_bp_terms.values()], key=lambda x: x['term']['display_name'].lower()),
#                                    'manual_cellular_component_terms': sorted([dict({'term': x.to_min_json(),
#                                                                                     'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
#                                                                                     'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
#                                                                                     }) for x in manual_cc_terms.values()], key=lambda x: x['term']['display_name'].lower()),
#                                    'htp_molecular_function_terms': sorted([dict({'term': x.to_min_json(),
#                                                                                  'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
#                                                                                  'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
#                                                                                     }) for x in htp_mf_terms.values()], key=lambda x: x['term']['display_name'].lower()),
#                                    'htp_biological_process_terms': sorted([dict({'term': x.to_min_json(),
#                                                                                  'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
#                                                                                  'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
#                                                                                     }) for x in htp_bp_terms.values()], key=lambda x: x['term']['display_name'].lower()),
#                                    'htp_cellular_component_terms': sorted([dict({'term': x.to_min_json(),
#                                                                                  'evidence_codes': [y.to_min_json() for y in term_to_evidence_codes_qualifiers[x.id][0]],
#                                                                                  'qualifiers': list(term_to_evidence_codes_qualifiers[x.id][1])
#                                                                                     }) for x in htp_cc_terms.values()], key=lambda x: x['term']['display_name'].lower())}
#
#         #Interaction
#         genetic_interactions = set()
#         physical_interactions = set()
#         genetic_interactions.update(self.geninteraction_evidences1)
#         genetic_interactions.update(self.geninteraction_evidences2)
#         physical_interactions.update(self.physinteraction_evidences1)
#         physical_interactions.update(self.physinteraction_evidences2)
#
#         genetic_bioentities = set([x.locus2_id if x.locus1_id == self.id else x.locus1_id for x in genetic_interactions])
#         physical_bioentities = set([x.locus2_id if x.locus1_id == self.id else x.locus1_id for x in physical_interactions])
#
#         A = len(genetic_bioentities)
#         B = len(physical_bioentities)
#         C = len(genetic_bioentities & physical_bioentities)
#         r, s, x = calc_venn_measurements(A, B, C)
#
#         physical_experiments = dict()
#         genetic_experiments = dict()
#         experiment_id_to_name = dict()
#
#         for genevidence in genetic_interactions:
#             experiment_id = genevidence.experiment_id
#             if experiment_id not in experiment_id_to_name:
#                 experiment_id_to_name[experiment_id] = genevidence.experiment.display_name
#             experiment_name = experiment_id_to_name[experiment_id]
#
#             if experiment_name not in genetic_experiments:
#                 genetic_experiments[experiment_name] = 1
#             else:
#                 genetic_experiments[experiment_name] += 1
#
#         for physevidence in physical_interactions:
#             experiment_id = physevidence.experiment_id
#             if experiment_id not in experiment_id_to_name:
#                 experiment_id_to_name[experiment_id] = physevidence.experiment.display_name
#             experiment_name = experiment_id_to_name[experiment_id]
#
#             if experiment_name not in physical_experiments:
#                 physical_experiments[experiment_name] = 1
#             else:
#                 physical_experiments[experiment_name] += 1
#
#         obj_json['interaction_overview'] = {'gen_circle_size': r, 'phys_circle_size':s, 'circle_distance': x,
#                                             'num_gen_interactors': A, 'num_phys_interactors': B, 'num_both_interactors': C,
#                                             'total_interactions': len(genetic_interactions) + len(physical_interactions),
#                                             'total_interactors': len(genetic_bioentities | physical_bioentities),
#                                             'physical_experiments': physical_experiments,
#                                             'genetic_experiments': genetic_experiments
#                                             }
#         #Regulation
#         regulation_paragraphs = [x.to_json(linkit=True) for x in self.paragraphs if x.category == 'REGULATION']
#
#         obj_json['regulation_overview'] = {'target_count': len(set([x.locus2_id for x in self.regulation_evidences_targets])),
#                                             'regulator_count':len(set([x.locus1_id for x in self.regulation_evidences_regulators])),
#                                             'paragraph': None if len(regulation_paragraphs) == 0 else regulation_paragraphs[0]}
#
#         #Literature
#         reference_ids = set([x.reference_id for x in self.literature_evidences])
#         reference_ids.update([x.reference_id for x in self.geninteraction_evidences1])
#         reference_ids.update([x.reference_id for x in self.geninteraction_evidences2])
#         reference_ids.update([x.reference_id for x in self.physinteraction_evidences1])
#         reference_ids.update([x.reference_id for x in self.physinteraction_evidences2])
#         reference_ids.update([x.reference_id for x in self.regulation_evidences_targets])
#         reference_ids.update([x.reference_id for x in self.regulation_evidences_regulators])
#         obj_json['literature_overview'] = {'total_count': len(reference_ids),
#                                            'primary_count': len(set([x.reference_id for x in self.literature_evidences if x.topic == 'Primary Literature'])),
#                                            'additional_count': len(set([x.reference_id for x in self.literature_evidences if x.topic == 'Additional Literature'])),
#                                            'review_count': len(set([x.reference_id for x in self.literature_evidences if x.topic == 'Reviews']))}
#
#         #Sequence
#         obj_json['sequence_overview'] = sorted(dict([(x.strain.id, x.strain.to_min_json()) for x in self.dnasequence_evidences]).values(), key=lambda x: x['display_name'])
#
#         reference_protein_sequence = None
#         for protein_sequence in self.proteinsequence_evidences:
#             if protein_sequence.strain_id == 1:
#                 reference_protein_sequence = protein_sequence
#         #Protein
#         obj_json['protein_overview'] = {
#             'length': None if reference_protein_sequence is None else len(reference_protein_sequence.residues)-1,
#             'molecular_weight': None if reference_protein_sequence is None else reference_protein_sequence.molecular_weight,
#             'pi': None if reference_protein_sequence is None else reference_protein_sequence.pi
#         }
#
#         #Aliases
#         obj_json['aliases'] = [x.to_json() for x in self.aliases]
#
#         #Urls
#         obj_json['urls'] = [x.to_json() for x in sorted(self.urls, key=lambda x: x.display_name) if x.category is not None and x.category != 'NONE']
#
#         lsp_paragraphs = [x.to_json(linkit=True) for x in self.paragraphs if x.category == 'LSP']
#         obj_json['paragraph'] = None if len(lsp_paragraphs) == 0 else lsp_paragraphs[0]
#
#         #History
#         note_to_evidences = dict()
#         for historyevidence in self.history_evidences:
#             if historyevidence.note in note_to_evidences:
#                 note_to_evidences[historyevidence.note].append(historyevidence)
#             else:
#                 note_to_evidences[historyevidence.note] = [historyevidence]
#
#         historyevidences = []
#         for note, evidences in note_to_evidences.iteritems():
#             evidence_json = evidences[0].to_json()
#             del evidence_json['reference']
#             evidence_json['references'] = [x.reference.to_min_json() for x in sorted(evidences, key=lambda y:None if y.reference is None else y.reference.year) if x.reference_id is not None]
#             historyevidences.append(evidence_json)
#
#
#         obj_json['history'] = historyevidences
#
#         obj_json['paralogs'] = [x.to_json() for x in self.children if x.relation_type == 'paralog']
#
#         obj_json['qualities'] = dict([(x.display_name.lower().replace(' ', '_'), x.to_json()) for x in self.qualities])
#
#         ordered_references = self.get_ordered_references()
#         obj_json['references'] = [x.to_semi_json() for x in ordered_references]
#         reference_mapping = {}
#         for reference in ordered_references:
#             reference_mapping[reference.id] = len(reference_mapping)+1
#
#         obj_json['reference_mapping'] = reference_mapping
#
#         if self.reserved_name is not None:
#             obj_json['reserved_name'] = self.reserved_name.to_json()
#
#         obj_json['pathways'] = [x.to_json() for x in self.pathway_evidences]
#
#         obj_json['ecnumbers'] = None if len(self.ecnumber_evidences) == 0 else [x.ecnumber.to_min_json() for x in self.ecnumber_evidences]
#
#         return obj_json