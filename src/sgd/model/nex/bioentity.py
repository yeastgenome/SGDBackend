from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from bioconcept import Go
from src.sgd.model.nex.misc import Alias, Url, Relation, Source
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

class Locus(Bioentity):
    __tablename__ = "locusbioentity"
    
    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    name_description = Column('name_description', String)
    headline = Column('headline', String)
    locus_type = Column('locus_type', String)
    gene_name = Column('gene_name', String)
        
    __mapper_args__ = {'polymorphic_identity': 'LOCUS', 'inherit_condition': id == Bioentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
                     'description',
                     'name_description', 'headline', 'locus_type', 'gene_name',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.link = None if obj_json.get('sgdid') is None else '/cgi-bin/locus.fpl?locus=' + obj_json.get('sgdid')

    def to_semi_json(self):
        obj_json = UpdateByJsonMixin.to_min_json(self)
        obj_json['description'] = self.description
        return obj_json

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)

        #Phenotype overview
        classical_groups = dict()
        large_scale_groups = dict()
        strain_groups = dict()
        for evidence in self.phenotype_evidences:
            if evidence.experiment.category == 'classical genetics':
                if evidence.mutant_type in classical_groups:
                    classical_groups[evidence.mutant_type] += 1
                else:
                    classical_groups[evidence.mutant_type] = 1
            elif evidence.experiment.category == 'large-scale survey':
                if evidence.mutant_type in large_scale_groups:
                    large_scale_groups[evidence.mutant_type] += 1
                else:
                    large_scale_groups[evidence.mutant_type] = 1

            if evidence.strain is not None:
                if evidence.strain.display_name in strain_groups:
                    strain_groups[evidence.strain.display_name] += 1
                else:
                    strain_groups[evidence.strain.display_name] = 1
        experiment_categories = []
        mutant_types = set(classical_groups.keys())
        mutant_types.update(large_scale_groups.keys())
        for mutant_type in mutant_types:
            experiment_categories.append([mutant_type, 0 if mutant_type not in classical_groups else classical_groups[mutant_type], 0 if mutant_type not in large_scale_groups else large_scale_groups[mutant_type]])
        strains = []
        for strain, count in strain_groups.iteritems():
            strains.append([strain, count])
        experiment_categories.sort(key=lambda x: x[1] + x[2], reverse=True)
        experiment_categories.insert(0, ['Mutant Type', 'classical genetics', 'large-scale survey'])
        strains.sort(key=lambda x: x[1], reverse=True)
        strains.insert(0, ['Strain', 'Annotations'])
        obj_json['phenotype_overview'] = {'experiment_categories': experiment_categories,
                                          'strains': strains}

        #Go overview
        go_paragraphs = [x.to_json() for x in self.paragraphs if x.category == 'GO']
        obj_json['go_overview'] = {'go_slim': sorted(dict([(x.id, x.to_min_json()) for x in chain(*[[x.parent for x in y.go.parents if x.relation_type == 'GO_SLIM'] for y in self.go_evidences])]).values(), key=lambda x: x['display_name']),
                                   'date_last_reviewed': None if len(go_paragraphs) == 0 else go_paragraphs[0]}

        #Interaction
        genetic_bioentities = set([x.locus2_id for x in self.geninteraction_evidences1])
        genetic_bioentities.update([x.locus1_id for x in self.geninteraction_evidences2])
        physical_bioentities = set([x.locus2_id for x in self.physinteraction_evidences1])
        physical_bioentities.update([x.locus1_id for x in self.physinteraction_evidences2 ])

        A = len(genetic_bioentities)
        B = len(physical_bioentities)
        C = len(genetic_bioentities & physical_bioentities)
        r, s, x = calc_venn_measurements(A, B, C)

        obj_json['interaction_overview'] = {'gen_circle_size': r, 'phys_circle_size':s, 'circle_distance': x,
                                            'num_gen_interactors': A, 'num_phys_interactors': B, 'num_both_interactors': C}
        #Regulation
        regulation_paragraphs = [x.to_json(linkit=True) for x in self.paragraphs if x.category == 'REGULATION']

        obj_json['regulation_overview'] = {'target_count': len(set([x.locus2_id for x in self.regulation_evidences_targets])),
                                            'regulator_count':len(set([x.locus1_id for x in self.regulation_evidences_regulators])),
                                            'paragraph': None if len(regulation_paragraphs) == 0 else regulation_paragraphs[0]}


        #Literature
        reference_ids = set([x.reference_id for x in self.literature_evidences])
        reference_ids.update([x.reference_id for x in self.geninteraction_evidences1])
        reference_ids.update([x.reference_id for x in self.geninteraction_evidences2])
        reference_ids.update([x.reference_id for x in self.physinteraction_evidences1])
        reference_ids.update([x.reference_id for x in self.physinteraction_evidences2])
        reference_ids.update([x.reference_id for x in self.regulation_evidences_targets])
        reference_ids.update([x.reference_id for x in self.regulation_evidences_regulators])
        obj_json['literature_overview'] = {'total_count': len(reference_ids)}

        #Sequence
        obj_json['sequence_overview'] = sorted(dict([(x.strain.id, x.strain.to_min_json()) for x in self.dnasequence_evidences]).values(), key=lambda x: x['display_name'])

        #Aliases
        obj_json['aliases'] = [x.to_json() for x in self.aliases]

        #Urls
        obj_json['urls'] = [x.to_json() for x in sorted(self.urls, key=lambda x: x.display_name)]

        return obj_json

class Complex(Bioentity):
    __tablename__ = 'complexbioentity'

    id = Column('bioentity_id', Integer, ForeignKey(Bioentity.id), primary_key = True)
    go_id = Column('go_id', Integer, ForeignKey(Go.id))
    cellular_localization = Column('cellular_localization', String)

    #Relationships
    go = relationship(Go, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "COMPLEX", 'inherit_condition': id==Bioentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'bioent_status',
                     'description',
                     'cellular_localization',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'go']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        go = obj_json.get('go')
        if go is not None:
            self.display_name = go.display_name
            self.format_name = create_format_name(go.display_name.lower())
            self.link = '/complex/' + self.format_name + '/overview'
            self.description = go.description

    @hybrid_property
    def genes(self):
        return [x for x in self.complex_evidences]

    @hybrid_property
    def child_genes(self):
        own_genes = self.genes
        for child_relation in self.children:
            own_genes.extend(child_relation.child.genes)
        return own_genes

    def to_semi_json(self):
        obj_json = UpdateByJsonMixin.to_min_json(self)
        obj_json['complex_evidences'] = [x.to_json() for x in self.genes]
        return obj_json

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['subcomplexes'] = [x.child.to_semi_json() for x in self.children]
        obj_json['aliases'] = [x.to_min_json() for x in self.aliases]
        obj_json['complex_evidences'] = [x.to_json() for x in self.genes]
        return obj_json