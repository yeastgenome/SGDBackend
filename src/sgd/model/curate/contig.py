from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Date, CLOB, Numeric

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.taxonomy import Taxonomy

__author__ = 'kelley'

class Contig(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'contig'

    id = Column('contig_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    residues = Column('residues', CLOB)
    taxonomy_id = Column('taxonomy_id', ForeignKey(Taxonomy.id))
    reference_chromosome_id = Column('reference_chromosome_id', Integer, ForeignKey('nex.contig.contig_id'))
    is_chromosome = Column('is_chromosome', Integer)
    centromere_start = Column('centromere_start', Integer)
    centromere_end = Column('centromere_end', Integer)
    genbank_accession = Column('genbank_accession', String)
    gi_number = Column('gi_number', String)
    refseq_id = Column('refseq_id', String)
    reference_start = Column('reference_start', Integer)
    reference_end = Column('reference_end', Integer)
    reference_percent_identity = Column('reference_percent_identity', Numeric(7, 3))
    reference_alignment_length = Column('reference_alignment_length', Integer)
    header = Column('header', String)
    filename = Column('filename', String)
    seq_version = Column('seq_version', Date)
    coord_version = Column('coord_version', Date)

    #Relationships
    source = relationship(Source, uselist=False)
    taxonomy = relationship(Taxonomy, uselist=False, backref='contigs')
    reference_chromosome = relationship('Contig', remote_side=[id])

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'bud_id', 'date_created', 'created_by',
                     'residues', 'centromere_start', 'centromere_end', 'is_chromosome', 'genbank_accession', 'gi_number', 'refseq_id',
                     'header', 'filename', 'reference_start', 'reference_end', 'reference_percent_identity', 'reference_alignment_length',
                     'seq_version', 'coord_version']
    __eq_fks__ = [('source', Source, False),
                  ('taxonomy', Taxonomy, False),
                  ('reference_chromosome', 'contig.Contig', False)]
    __id_values__ = ['id', 'display_name', 'genbank_accession', 'gi_number', 'refseq_id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['reference_chromosome_id', 'seq_version', 'coord_version', 'taxonomy_id']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_display_name__(cls, obj_json):
        return obj_json['genbank_accession'] if 'display_name' not in obj_json else obj_json['display_name']

    # def to_min_json(self, include_description=False):
    #     obj_json = UpdateWithJsonMixin.to_min_json(self, include_description=include_description)
    #     obj_json['length'] = len(self.residues)
    #     obj_json['is_chromosome'] = True if self.is_chromosome == 1 else False
    #     obj_json['centromere_start'] = self.centromere_start
    #     obj_json['centromere_end'] = self.centromere_end
    #     return obj_json
    #
    # def to_semi_json(self):
    #     obj_json = self.to_min_json()
    #     obj_json['reference_alignment'] = None if self.reference_chromosome_id is None else \
    #         {'chromosome': self.reference_chromosome.to_min_json(),
    #          'start': self.reference_start,
    #          'end': self.reference_end,
    #          'percent_identity': str(self.reference_percent_identity),
    #          'alignment_length': self.reference_alignment_length
    #         }
    #     obj_json['genbank_accession'] = self.genbank_accession
    #     obj_json['refseq_id'] = self.refseq_id
    #     obj_json['urls'] = [x.to_min_json() for x in self.urls]
    #     obj_json['length'] = len(self.residues)
    #     return obj_json
    #
    # def to_json(self):
    #     obj_json = UpdateWithJsonMixin.to_json(self)
    #     overview_counts = {}
    #     for evidence in [x for x in self.dnasequence_evidences if x.dna_type== 'GENOMIC']:
    #         if x.locus.bioent_status == 'Active':
    #             if evidence.locus.locus_type in overview_counts:
    #                 overview_counts[evidence.locus.locus_type] += 1
    #             else:
    #                 overview_counts[evidence.locus.locus_type] = 1
    #
    #     obj_json['overview'] = [
    #         ['Feature Type', 'Count']]
    #
    #     for locus_type in locus_types:
    #         obj_json['overview'].append([locus_type, (0 if locus_type not in overview_counts else overview_counts[locus_type])])
    #
    #     obj_json['urls'] = [x.to_min_json() for x in self.urls]
    #
    #     return obj_json
