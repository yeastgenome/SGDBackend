from sqlalchemy import ForeignKey, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin
from src.sgd.model.nex.misc import Source, Relation, Strain, Url, Alias, Tag
from src.sgd.model.nex.reference import Reference
from decimal import Decimal

__author__ = 'kpaskov'

class Bioitem(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'bioitem'
    
    id = Column('bioitem_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    description = Column('description', String)
    bioitem_type = Column('bioitem_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    
    __mapper_args__ = {'polymorphic_on': class_type}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def unique_key(self):
        return self.format_name, self.class_type

    def to_min_json(self, include_description=False):
        obj_json = UpdateByJsonMixin.to_min_json(self, include_description=include_description)
        obj_json['class_type'] = self.class_type
        return obj_json

class Bioitemrelation(Relation):
    __tablename__ = 'bioitemrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Bioitem.id))
    child_id = Column('child_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    parent = relationship(Bioitem, backref=backref("children", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Bioitem, backref=backref("parents", passive_deletes=True), uselist=False, foreign_keys=[child_id])

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Relation.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'relation_type',
                     'parent_id', 'child_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))
        self.display_name = str(obj_json.get('parent_id')) + ' - ' + str(obj_json.get('child_id'))

class Bioitemurl(Url):
    __tablename__ = 'bioitemurl'

    id = Column('url_id', Integer, ForeignKey(Url.id), primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False, backref=backref('urls', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Url.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioitem_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioitem_id'))

class Bioitemalias(Alias):
    __tablename__ = 'bioitemalias'

    id = Column('alias_id', Integer, ForeignKey(Alias.id), primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False, backref=backref('aliases', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'BIOITEM', 'inherit_condition': id == Alias.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'category',
                     'bioitem_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = str(obj_json.get('bioitem_id'))

class BioitemTag(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'bioitem_tag'

    id = Column('bioitem_tag_id', Integer, primary_key=True)
    bioitem_id = Column('bioitem_id', Integer, ForeignKey(Bioitem.id))
    tag_id = Column('tag_id', Integer, ForeignKey(Tag.id))

    #Relationships
    bioitem = relationship(Bioitem, uselist=False, backref=backref('bioitem_tags', passive_deletes=True))
    tag = relationship(Tag, uselist=False, backref=backref('bioitem_tags', passive_deletes=True))

    __eq_values__ = ['id']
    __eq_fks__ = ['bioitem', 'tag']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    def unique_key(self):
        return self.bioitem_id, self.tag_id

class Domain(Bioitem):
    __tablename__ = "domainbioitem"
    
    id = Column('bioitem_id', Integer, primary_key=True)
    interpro_id = Column('interpro_id', String)
    interpro_description = Column('interpro_description', String)

    __mapper_args__ = {'polymorphic_identity': 'DOMAIN', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'interpro_id', 'interpro_description',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']
    
    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))
        self.link = None if self.format_name is None else '/domain/' + self.format_name + '/overview'

    @hybrid_property
    def count(self):
        return len(set([x.locus_id for x in self.domain_evidences]))

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        return obj_json

class Chemical(Bioitem):
    __tablename__ = "chemicalbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    chebi_id = Column('chebi_id', String)

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'chebi_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))[:95]
        self.link = None if self.format_name is None else '/chemical/' + self.format_name + '/overview'

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        return obj_json


number_to_roman = {'01': 'I', '1': 'I',
                   '02': 'II', '2': 'II',
                   '03': 'III', '3': 'III',
                   '04': 'IV', '4': 'IV',
                   '05': 'V', '5': 'V',
                   '06': 'VI', '6': 'VI',
                   '07': 'VII', '7': 'VII',
                   '08': 'VIII', '8': 'VIII',
                   '09': 'IX', '9': 'IX',
                   '10': 'X',
                   '11': 'XI',
                   '12': 'XII',
                   '13': 'XIII',
                   '14': 'XIV',
                   '15': 'XV',
                   '16': 'XVI',
                   '17': 'Mito',
                   }

class Contig(Bioitem):
    __tablename__ = "contigbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    residues = Column('residues', CLOB)
    strain_id = Column('strain_id', ForeignKey(Strain.id))

    #Relationships
    strain = relationship(Strain, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "CONTIG", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'residues',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'strain']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('strain') is None or create_format_name(obj_json.get('display_name')) is None else obj_json.get('strain').format_name + '_' + create_format_name(obj_json.get('display_name'))
        self.link = None if self.format_name is None else '/contig/' + self.format_name + '/overview'
        if self.display_name.startswith('chr'):
            self.display_name = 'Chromosome ' + (self.display_name[3:] if self.display_name[3:] not in number_to_roman else number_to_roman[self.display_name[3:]])
        if self.display_name.startswith('Chromosome '):
            self.display_name = 'Chromosome ' + (self.display_name[11:] if self.display_name[11:] not in number_to_roman else number_to_roman[self.display_name[11:]])

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        overview_counts = {}
        for evidence in [x for x in self.dnasequence_evidences if x.dna_type== 'GENOMIC']:
            if x.locus.bioent_status == 'Active':
                if evidence.locus.locus_type in overview_counts:
                    overview_counts[evidence.locus.locus_type] += 1
                else:
                    overview_counts[evidence.locus.locus_type] = 1

        obj_json['overview'] = [
            ['Feature Type', 'Count'],
            ['ORF', (0 if 'ORF' not in overview_counts else overview_counts['ORF'])],
            ['long_terminal_repeat', (0 if 'long_terminal_repeat' not in overview_counts else overview_counts['long_terminal_repeat'])],
            ['ARS', (0 if 'ARS' not in overview_counts else overview_counts['ARS'])],
            ['tRNA', (0 if 'tRNA' not in overview_counts else overview_counts['tRNA'])],
            ['transposable_element_gene', (0 if 'transposable_element_gene' not in overview_counts else overview_counts['transposable_element_gene'])],
            ['snoRNA', (0 if 'snoRNA' not in overview_counts else overview_counts['snoRNA'])],
            ['retrotransposon', (0 if 'retrotransposon' not in overview_counts else overview_counts['retrotransposon'])],
            ['telomere', (0 if 'telomere' not in overview_counts else overview_counts['telomere'])],
            ['rRNA', (0 if 'rRNA' not in overview_counts else overview_counts['rRNA'])],
            ['pseudogene', (0 if 'pseudogene' not in overview_counts else overview_counts['pseudogene'])],
            ['ncRNA', (0 if 'ncRNA' not in overview_counts else overview_counts['ncRNA'])],
            ['centromere', (0 if 'centromere' not in overview_counts else overview_counts['centromere'])],
            ['snRNA', (0 if 'snRNA' not in overview_counts else overview_counts['snRNA'])],
            ['multigene locus', (0 if 'multigene locus' not in overview_counts else overview_counts['multigene locus'])],
            ['gene_cassette', (0 if 'gene_cassette' not in overview_counts else overview_counts['gene_cassette'])],
            ['mating_locus', (0 if 'mating_locus' not in overview_counts else overview_counts['mating_locus'])]]

        return obj_json

class Dataset(Bioitem):
    __tablename__ = "datasetbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    geo_id = Column('geo_id', String)
    pcl_filename = Column('pcl_filename', String)
    short_description = Column('short_description', String)
    channel_count = Column('channel_count', Integer)
    condition_count = Column('condition_count', Integer)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))

    #Relationships
    reference = relationship(Reference, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "DATASET", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'geo_id', 'pcl_filename', 'short_description', 'channel_count', 'condition_count',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = obj_json.get('pcl_filename')[:-4]
        self.display_name = self.format_name
        self.link = '/dataset/' + self.format_name + '/overview'

    def to_semi_json(self):
        obj_json = UpdateByJsonMixin.to_min_json(self)
        obj_json['pcl_filename'] = self.pcl_filename
        obj_json['geo_id'] = self.geo_id
        obj_json['short_description'] = self.short_description
        obj_json['condition_count'] = self.condition_count
        obj_json['reference'] = None if self.reference is None else self.reference.to_min_json()
        obj_json['tags'] = [x.tag.to_min_json() for x in self.bioitem_tags]
        obj_json['display_name'] = self.display_name.replace('.', '. ')
        return obj_json

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['reference'] = None if self.reference is None else self.reference.to_json()
        obj_json['datasetcolumns'] = [x.to_min_json() for x in self.datasetcolumns]
        obj_json['tags'] = [x.tag.to_min_json() for x in self.bioitem_tags]
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        return obj_json

class Datasetcolumn(Bioitem):
    __tablename__ = "datasetcolumnbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    file_order = Column('file_order', Integer)
    dataset_id = Column('dataset_id', Integer, ForeignKey(Dataset.id))

    #Relationships
    dataset = relationship(Dataset, uselist=False, backref='datasetcolumns')

    __mapper_args__ = {'polymorphic_identity': "DATASETCOLUMN", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'file_order', 'dataset_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'dataset']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = obj_json.get('dataset').format_name + '.' + str(obj_json.get('file_order'))
        self.display_name = obj_json.get('description')

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['dataset'] = self.dataset.to_min_json()
        return obj_json

class Allele(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ALLELE', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))

class Orphanbioitem(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'ORPHAN', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))
