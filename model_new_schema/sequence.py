import hashlib

__author__ = 'kpaskov'

from model_new_schema import Base, EqualityByIDMixin
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric, CLOB

class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'sequence'

    id = Column('sequence_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('subclass', String)
    residues = Column('residues', CLOB)
    length = Column('length', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type}

    def __init__(self, display_name, format_name, class_type, residues,
                 date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.residues = residues
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.format_name, self.class_type)

class Dnasequence(Sequence):
    __mapper_args__ = {'polymorphic_identity': "DNA",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, residues):
        hash = hashlib.md5(residues).hexdigest()[:10]
        Sequence.__init__(self, 'Sequence: ' + hash, hash, 'DNA', residues, None, None)

class Rnasequence(Sequence):
    __mapper_args__ = {'polymorphic_identity': "RNA",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, residues):
        hash = hashlib.md5(residues).hexdigest()[:10]
        Sequence.__init__(self, 'Sequence: ' + hash, hash, 'RNA', residues, None, None)

class Proteinsequence(Sequence):
    __tablename__ = "proteinsequence"

    id = Column('sequence_id', Integer, ForeignKey(Sequence.id), primary_key=True)

    molecular_weight = Column('molecular_weight', Integer)
    pi = Column('pi', Numeric)

    #amino acid composition
    ala = Column('ala', Integer)
    arg = Column('arg', Integer)
    asn = Column('asn', Integer)
    asp = Column('asp', Integer)
    cys = Column('cys', Integer)
    gln = Column('gln', Integer)
    glu = Column('glu', Integer)
    gly = Column('gly', Integer)
    his = Column('his', Integer)
    ile = Column('ile', Integer)
    leu = Column('leu', Integer)
    lys = Column('lys', Integer)
    met = Column('met', Integer)
    phe = Column('phe', Integer)
    pro = Column('pro', Integer)
    ser = Column('ser', Integer)
    thr = Column('thr', Integer)
    trp = Column('trp', Integer)
    tyr = Column('tyr', Integer)
    val = Column('val', Integer)

    #atomic composition
    carbon = Column('carbon', Integer)
    hydrogen = Column('hydrogen', Integer)
    nitrogen = Column('nitrogen', Integer)
    oxygen = Column('oxygen', Integer)
    sulfur = Column('sulfur', Integer)

    #estimated half-life
    ecoli_vivo = Column('ecoli_vivo', String)
    mammal_vitro = Column('mammal_vitro', String)
    yeast_vivo = Column('yeast_vivo', String)

    #extinction coefficients at 280nm
    all_cys_half = Column('all_cys_half', String)
    no_cys_half = Column('no_cys_half', String)
    all_cys_reduced = Column('all_cys_reduced', String)
    all_cys = Column('all_cys', String)

    aliphatic_index = Column('aliphatic_index', Numeric)
    instability_index = Column('instability_index', Numeric)

    codon_bias = Column('codon_bias', Numeric)
    codon_adaptation_index = Column('cai', Numeric)
    frequency_of_optimal_codons = Column('fop', Numeric)
    hydropathicity = Column('hydropathicity', Numeric)
    aromaticity_score = Column('aromaticity_score', Numeric)

    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Sequence.id}

    def __init__(self, residues, date_created=None, created_by=None):
        hash = hashlib.md5(residues).hexdigest()[:10]
        Sequence.__init__(self, 'Sequence: ' + hash, hash,
                           'PROTEIN', residues, date_created, created_by)
