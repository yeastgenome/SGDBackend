from sqlalchemy import ForeignKey, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric
from sqlalchemy.ext.hybrid import hybrid_property

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name, UpdateByJsonMixin, locus_types
from src.sgd.model.nex.misc import Source, Relation, Strain, Url, Alias, Tag
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.bioentity import Locus
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

class Contig(Bioitem):
    __tablename__ = "contigbioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    residues = Column('residues', CLOB)
    strain_id = Column('strain_id', ForeignKey(Strain.id))
    is_chromosome = Column('is_chromosome', Integer)
    centromere_start = Column('centromere_start', Integer)
    centromere_end = Column('centromere_end', Integer)
    genbank_accession = Column('genbank_accession', String)
    gi_number = Column('gi_number', String)
    refseq_id = Column('refseq_id', String)
    reference_chromosome_id = Column('reference_chromosome_id', Integer, ForeignKey('nex.contigbioitem.bioitem_id'))
    reference_start = Column('reference_start', Integer)
    reference_end = Column('reference_end', Integer)
    reference_percent_identity = Column('reference_percent_identity', Numeric(7, 3))
    reference_alignment_length = Column('reference_alignment_length', Integer)
    #header = Column('header', String)
    #filename = Column('filename', String)

    #Relationships
    strain = relationship(Strain, uselist=False, backref='contigs')
    reference_chromosome = relationship('Contig', remote_side=[id])

    __mapper_args__ = {'polymorphic_identity': "CONTIG", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'residues', 'centromere_start', 'centromere_end', 'is_chromosome', 'genbank_accession', 'gi_number', 'refseq_id',
                     #'header', 'filename',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'strain']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        if self.format_name is None:
            self.format_name = self.genbank_accession
        if self.display_name is None:
            self.display_name = self.genbank_accession
        self.link = None if self.format_name is None else '/contig/' + self.format_name + '/overview'

    def to_min_json(self, include_description=False):
        obj_json = UpdateByJsonMixin.to_min_json(self, include_description=include_description)
        obj_json['length'] = len(self.residues)
        obj_json['is_chromosome'] = True if self.is_chromosome == 1 else False
        obj_json['centromere_start'] = self.centromere_start
        obj_json['centromere_end'] = self.centromere_end
        return obj_json

    def to_semi_json(self):
        obj_json = self.to_min_json()
        obj_json['reference_alignment'] = None if self.reference_chromosome_id is None else \
            {'chromosome': self.reference_chromosome.to_min_json(),
             'start': self.reference_start,
             'end': self.reference_end,
             'percent_identity': str(self.reference_percent_identity),
             'alignment_length': self.reference_alignment_length
            }
        obj_json['genbank_accession'] = self.genbank_accession
        obj_json['refseq_id'] = self.refseq_id
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        obj_json['length'] = len(self.residues)
        return obj_json

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
            ['Feature Type', 'Count']]

        for locus_type in locus_types:
            obj_json['overview'].append([locus_type, (0 if locus_type not in overview_counts else overview_counts[locus_type])])

        obj_json['urls'] = [x.to_min_json() for x in self.urls]

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
    geo_id = Column('geo_id', String)
    dataset_id = Column('dataset_id', Integer, ForeignKey(Dataset.id))

    #Relationships
    dataset = relationship(Dataset, uselist=False, backref='datasetcolumns')

    __mapper_args__ = {'polymorphic_identity': "DATASETCOLUMN", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'file_order', 'geo_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'dataset']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = obj_json.get('dataset').format_name + '.' + str(obj_json.get('file_order'))
        self.display_name = obj_json.get('description')

    def to_min_json(self, include_description=False):
        obj_json = UpdateByJsonMixin.to_min_json(self, include_description=include_description)
        obj_json['geo_id'] = self.geo_id
        return obj_json

    def to_json(self):
        obj_json = UpdateByJsonMixin.to_json(self)
        obj_json['dataset'] = self.dataset.to_min_json()
        return obj_json

class Reservedname(Bioitem):
    __tablename__ = "reservednamebioitem"

    id = Column('bioitem_id', Integer, primary_key=True)
    locus_id = Column('locus_id', ForeignKey(Locus.id))
    reference_id = Column('reference_id', ForeignKey(Reference.id))
    reservation_date = Column('reservation_date', Date)
    expiration_date = Column('expiration_date', Date)

    #Relationships
    locus = relationship(Locus, uselist=False, backref=backref('reserved_name', uselist=False))
    reference = relationship(Reference, uselist=False)

    __mapper_args__ = {'polymorphic_identity': "RESERVEDNAME", 'inherit_condition': id==Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'reservation_date', 'expiration_date',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'locus', 'reference']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = self.display_name
        self.link = '/reserved_name/' + self.format_name + '/overview'

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

class Pathway(Bioitem):
    __mapper_args__ = {'polymorphic_identity': 'PATHWAY', 'inherit_condition': id == Bioitem.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'description', 'bioitem_type',
                     'date_created', 'created_by']
    __eq_fks__ = ['source']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
