__author__ = 'kpaskov'

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model.nex import Base, BasicObject, create_format_name, UpdateByJsonMixin, number_to_roman, eco_id_to_category
from src.sgd.model.nex.primary import Reference, Strain

class Secondary(Base, BasicObject):
    __tablename__ = 'secondaryobject'

    id = Column('id', Integer, primary_key=True)
    class_type = Column('subclass', String)
    is_root = Column('is_root', Integer, default=False)
    primary_count = Column('primary_count', Integer, default=0)
    descendant_primary_count = Column('descendant_primary_count', Integer, default=0)
    source_id = Column('source_id', Integer, ForeignKey('source.id'))

    #Relationships
    source = relationship('Source', uselist=False, lazy='joined')
    tags = association_proxy('secondary_tags', 'tag')

    __mapper_args__ = {'polymorphic_on': class_type}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root']
    __fks__ = ['source', 'urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']

    def unique_key(self):
        return self.class_type, self.format_name


class ECNumber(Secondary):
    __tablename__ = "ecnumber"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'ECNUMBER', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'uniprotid', 'name_description', 'headline', 'locus_type', 'gene_name', 'qualifier', 'genetic_position']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.link = None if self.display_name is None else '/ecnumber/' + self.display_name + '/overview'
        self.format_name = self.display_name

    @hybrid_property
    def annotations(self):
        return self.ecnumber_annotations


class Go(Secondary):
    __tablename__ = 'go'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    go_id = Column('go_id', String)
    go_aspect = Column('go_aspect', String)

    __mapper_args__ = {'polymorphic_identity': 'GO', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'go_id', 'go_aspect']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if self.display_name == 'biological_process':
            self.display_name = 'biological process'
            self.link = '/ontology/go/biological_process/overview'
            self.format_name = 'biological_process'
            self.is_root = True
        elif self.display_name == 'molecular_function':
            self.display_name = 'molecular function'
            self.link = '/ontology/go/molecular_function/overview'
            self.format_name = 'molecular_function'
            self.is_root = True
        elif self.display_name == 'cellular_component':
            self.display_name = 'cellular component'
            self.link = '/ontology/go/cellular_component/overview'
            self.format_name = 'cellular_component'
            self.is_root = True
        else:
            self.link = None if self.go_id is None else '/go/' + self.go_id + '/overview'
            self.format_name = self.go_id

    @hybrid_property
    def annotations(self):
        return self.go_annotations


class Observable(Secondary):
    __tablename__ = "observable"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    ancestor_type = Column('ancestor_type', String)

    __mapper_args__ = {'polymorphic_identity': 'OBSERVABLE', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'ancestor_type']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if self.display_name == 'observable':
            self.display_name = 'Yeast Phenotype Ontology'
            self.format_name = 'ypo'
            self.link = '/ontology/phenotype/ypo/overview'
            self.is_root = True
        else:
            self.format_name = None if self.display_name is None else create_format_name(self.display_name.lower())
            self.link = None if self.format_name is not None else '/observable/' + self.format_name + '/overview'

    @hybrid_property
    def annotations(self):
        return set(sum([x.phenotype_annotations for x in self.phenotypes], []))


class Phenotype(Secondary):
    __tablename__ = "phenotype"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    observable_id = Column('observable_id', Integer, ForeignKey(Observable.id))
    qualifier = Column('qualifier', String)

    #Relationships
    observable = relationship(Observable, uselist=False, foreign_keys=[observable_id], lazy='joined', backref=backref('phenotypes', passive_deletes=True))

    __mapper_args__ = {'polymorphic_identity': 'PHENOTYPE', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'qualifier']
    __fks__ = ['source', 'observable', 'urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = None if self.display_name is None else Phenotype.create_phenotype_display_name(obj_json['observable'].display_name, self.qualifier)
        self.format_name = None if obj_json['observable'] is None else Phenotype.create_phenotype_format_name(obj_json['observable'].display_name, self.qualifier)
        self.link = None if self.format_name is None else '/phenotype/' + self.format_name + '/overview'

    @hybrid_property
    def annotations(self):
        return self.phenotype_annotations

    @staticmethod
    def create_phenotype_display_name(observable, qualifier):
        if qualifier is None:
            display_name = observable
        else:
            display_name = observable + ': ' + qualifier
        return display_name

    @staticmethod
    def create_phenotype_format_name(observable, qualifier):
        if qualifier is None:
            format_name = create_format_name(observable.lower())
        else:
            observable = '.' if observable is None else observable
            qualifier = '.' if qualifier is None else qualifier
            format_name = create_format_name(qualifier.lower() + '_' + observable.lower())
        return format_name

class Domain(Secondary):
    __tablename__ = "domain"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    interpro_id = Column('interpro_id', String)
    interpro_description = Column('interpro_description', String)

    __mapper_args__ = {'polymorphic_identity': 'DOMAIN', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'interpro_id', 'interpro_description']


    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)
        self.link = None if self.format_name is None else '/domain/' + self.format_name + '/overview'

    @hybrid_property
    def annotations(self):
        return self.proteindomain_annotations


class Chemical(Secondary):
    __tablename__ = "chemical"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    chebi_id = Column('chebi_id', String)

    __mapper_args__ = {'polymorphic_identity': 'CHEMICAL', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'chebi_id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)[:95]
        self.link = None if self.format_name is None else '/chemical/' + self.format_name + '/overview'

    @hybrid_property
    def annotations(self):
        return self.phenotype_annotations


class Contig(Secondary):
    __tablename__ = "contig"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    residues = Column('residues', CLOB)
    strain_id = Column('strain_id', ForeignKey(Strain.id))
    is_chromosome = Column('is_chromosome', Integer)
    centromere_start = Column('centromere_start', Integer)
    centromere_end = Column('centromere_end', Integer)

    #Relationships
    strain = relationship(Strain, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'CONTIG', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'residues', 'centromere_start', 'centromere_end', 'is_chromosome']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type',
                    'length', 'is_chromosome', 'centromere_start', 'centromere_end']
    __fks__ = ['source', 'strain', 'urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('strain') is None or create_format_name(self.display_name) is None else obj_json.get('strain').format_name + '_' + create_format_name(self.display_name)
        self.link = None if self.format_name is None else '/contig/' + self.format_name + '/overview'
        if self.display_name.startswith('chr'):
            self.display_name = 'Chromosome ' + (self.display_name[3:] if self.display_name[3:] not in number_to_roman else number_to_roman[self.display_name[3:]])
        if self.display_name.startswith('Chromosome '):
            self.display_name = 'Chromosome ' + (self.display_name[11:] if self.display_name[11:] not in number_to_roman else number_to_roman[self.display_name[11:]])

    @hybrid_property
    def length(self):
        return len(self.residues)

    @hybrid_property
    def annotations(self):
        return self.sequence_annotations


class Dataset(Secondary):
    __tablename__ = "dataset"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    geo_id = Column('geo_id', String)
    pcl_filename = Column('pcl_filename', String)
    short_description = Column('short_description', String)
    channel_count = Column('channel_count', Integer)
    condition_count = Column('condition_count', Integer)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id))

    #Relationships
    reference = relationship(Reference, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'DATASET', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'geo_id', 'pcl_filename', 'short_description', 'channel_count', 'condition_count']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type',
                    'geo_id', 'pcl_filename', 'short_description', 'channel_count', 'condition_count']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type', 'description',
                     'geo_id', 'pcl_filename', 'short_description', 'condition_count']
    __fks__ = ['source', 'reference', 'datasetcolumns', 'urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']
    __semi_fks__ = ['reference', 'tags']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.pcl_filename is None else self.pcl_filename[:-4]
        self.display_name = self.format_name
        self.link = None if self.format_name is None else '/dataset/' + self.format_name + '/overview'

    @hybrid_property
    def annotations(self):
        return None


class Datasetcolumn(Secondary):
    __tablename__ = "datasetcolumn"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    file_order = Column('file_order', Integer)
    geo_id = Column('geo_id', String)
    dataset_id = Column('dataset_id', Integer, ForeignKey(Dataset.id))

    #Relationships
    dataset = relationship(Dataset, uselist=False, backref='datasetcolumns', foreign_keys=[dataset_id])

    __mapper_args__ = {'polymorphic_identity': 'DATASETCOLUMN', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                     'file_order', 'geo_id']
    __min_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type',
                    'file_order', 'geo_id']
    __semi_keys__ = ['id', 'display_name', 'format_name', 'link', 'class_type', 'description',
                     'geo_id']
    __fks__ = ['source', 'dataset', 'urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json['dataset'] is None else obj_json.get('dataset').format_name + '.' + str(obj_json.get('file_order'))
        self.display_name = self.description

    @hybrid_property
    def annotations(self):
        return None


class Reservedname(Secondary):
    __tablename__ = "reservedname"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey('locus.id'))
    reference_id = Column('reference_id', Integer, ForeignKey('reference.id'))

    #Relationships
    locus = relationship('Locus', uselist=False, backref='reserved_names')
    reference_id = relationship('Reference', uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'RESERVEDNAME', 'inherit_condition': id == Secondary.id}
    __fks__ = ['source', 'locus', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = self.display_name
        self.link = None if self.format_name is not None else '/reserved_name/' + self.format_name + '/overview'

    @hybrid_property
    def annotations(self):
        return self.reservedname_annotations


class Allele(Secondary):
    __tablename__ = "allele"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'ALLELE', 'inherit_condition': id == Secondary.id}

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if obj_json.get('display_name') is None else create_format_name(obj_json.get('display_name'))

    @hybrid_property
    def annotations(self):
        return self.allele_annotations


class Orphan(Secondary):
    __tablename__ = "orphan"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'ORPHAN', 'inherit_condition': id == Secondary.id}

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)

    @hybrid_property
    def annotations(self):
        return None


class Pathway(Secondary):
    __tablename__ = "pathway"

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'PATHWAY', 'inherit_condition': id == Secondary.id}

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)

    @hybrid_property
    def annotations(self):
        return self.pathway_annotations


class Source(Secondary):
    __tablename__ = 'source'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'SOURCE', 'inherit_condition': id == Secondary.id}
    __fks__ = ['urls', 'aliases', 'relations', 'qualities', 'annotations', 'tags']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)

    @hybrid_property
    def annotations(self):
        return None


class Experiment(Secondary):
    __tablename__ = 'experiment'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    eco_id = Column('eco_id', String)
    category = Column('category', String)

    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                'eco_id', 'category']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)
        self.category = None if self.eco_id not in eco_id_to_category else eco_id_to_category[self.eco_id]

    @hybrid_property
    def annotations(self):
        return None

class Book(Secondary):
    __tablename__ = 'book'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    title = Column('title', String)
    volume_title = Column('volume_title', String)
    isbn = Column('isbn', String)
    total_pages = Column('total_pages', Integer)
    publisher = Column('publisher', String)
    publisher_location = Column('publisher_location', String)

    __mapper_args__ = {'polymorphic_identity': 'BOOK', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                'title', 'volume_title', 'isbn', 'total_pages', 'publisher', 'publisher_location']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = self.title
        self.format_name = None if self.title is None else create_format_name(self.title + '' if self.volume_title is None else ('_' + self.volume_title))


class Journal(Secondary):
    __tablename__ = 'journal'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    title = Column('title', String)
    med_abbr = Column('med_abbr', String)
    issn_print = Column('issn_print', String)
    issn_online = Column('issn_online', String)

    __mapper_args__ = {'polymorphic_identity': 'JOURNAL', 'inherit_condition': id == Secondary.id}
    __keys__ = ['id', 'display_name', 'format_name', 'link', 'description', 'date_created', 'created_by', 'class_type', 'primary_count', 'descendant_primary_count', 'is_root',
                'title', 'med_abbr', 'issn_print', 'issn_online']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = self.title if self.title is not None else self.med_abbr
        self.format_name = None if self.display_name is None else create_format_name(self.display_name[:99] if self.med_abbr is None else self.display_name[:50] + '_' + self.med_abbr[:49])


class Author(Secondary):
    __tablename__ = 'author'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'AUTHOR', 'inherit_condition': id == Secondary.id}

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)
        self.link = None if self.format_name is None else '/author/' + self.format_name + '/overview'


class Reftype(Secondary):
    __tablename__ = 'reftype'

    id = Column('id', Integer, ForeignKey(Secondary.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'REFTYPE', 'inherit_condition': id == Secondary.id}

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = None if self.display_name is None else create_format_name(self.display_name)
