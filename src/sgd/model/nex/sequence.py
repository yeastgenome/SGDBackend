import hashlib

from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base

__author__ = 'kpaskov'

class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'biosequence'

    id = Column('biosequence_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    class_type = Column('subclass', String)
    residues = Column('residues', CLOB)
    length = Column('length', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type}

    def __init__(self, display_name, format_name, link, class_type, residues,
                 date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.link = link
        self.class_type = class_type
        self.residues = residues
        self.length = len(residues)
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.format_name, self.class_type)

class Dnasequence(Sequence):
    __mapper_args__ = {'polymorphic_identity': "DNA",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, residues):
        hash = hashlib.md5(residues).hexdigest()
        Sequence.__init__(self, 'Sequence: ' + hash, hash, None, 'DNA', residues, None, None)

class Rnasequence(Sequence):
    __mapper_args__ = {'polymorphic_identity': "RNA",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, residues):
        hash = hashlib.md5(residues).hexdigest()
        Sequence.__init__(self, 'Sequence: ' + hash, hash, None, 'RNA', residues, None, None)

class Proteinsequence(Sequence):
    __tablename__ = "proteinbiosequence"

    id = Column('biosequence_id', Integer, ForeignKey(Sequence.id), primary_key=True)
    molecular_weight = Column('molecular_weight', Numeric)
    pi = Column('pi', Numeric)
    cai = Column('cai', Numeric)
    n_term_seq = Column('n_term_seq', String)
    c_term_seq = Column('c_term_seq', String)
    codon_bias = Column('codon_bias', Numeric)
    fop_score = Column('fop_score', Numeric)
    gravy_score = Column('gravy_score', Numeric)
    aromaticity_score = Column('aromaticity_score', Numeric)
    aliphatic_index = Column('aliphatic_index', Numeric)
    instability_index = Column('instability_index', Numeric)

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
    thr = Column('thr', Integer)
    ser = Column('ser', Integer)
    trp = Column('trp', Integer)
    tyr = Column('tyr', Integer)
    val = Column('val', Integer)

    hydrogen = Column('hydrogen', Integer)
    sulfur = Column('sulfur', Integer)
    nitrogen = Column('nitrogen', Integer)
    oxygen = Column('oxygen', Integer)
    carbon = Column('carbon', Integer)

    yeast_half_life = Column('yeast_half_life', String)
    ecoli_half_life = Column('ecoli_half_life', String)
    mammal_half_life = Column('mammal_half_life', String)

    no_cys_ext_coeff = Column('no_cys_ext_coeff', String)
    all_cys_ext_coeff = Column('all_cys_ext_coeff', String)
    all_half_cys_ext_coeff = Column('all_half_cys_ext_coeff', String)
    all_pairs_cys_ext_coeff = Column('all_pairs_cys_ext_coeff', String)

    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Sequence.id}

    def __init__(self, residues, date_created=None, created_by=None):
        hash = hashlib.md5(residues).hexdigest()
        Sequence.__init__(self, 'Sequence: ' + hash, str(hash), None,
                           'PROTEIN', residues, date_created, created_by)
        self.n_term_seq = residues[0:7]
        self.c_term_seq = residues[-8:-1]
        self.ala = residues.count('A')
        self.arg = residues.count('R')
        self.asn = residues.count('N')
        self.asp = residues.count('D')
        self.cys = residues.count('C')
        self.gln = residues.count('Q')
        self.glu = residues.count('E')
        self.gly = residues.count('G')
        self.his = residues.count('H')
        self.ile = residues.count('I')
        self.leu = residues.count('L')
        self.lys = residues.count('K')
        self.met = residues.count('M')
        self.phe = residues.count('F')
        self.pro = residues.count('P')
        self.thr = residues.count('T')
        self.ser = residues.count('S')
        self.trp = residues.count('W')
        self.tyr = residues.count('Y')
        self.val = residues.count('V')

class Contig(Sequence):
    __mapper_args__ = {'polymorphic_identity': "CONTIG",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, display_name, residues, strain):
        format_name = strain.format_name + '_' + display_name
        Sequence.__init__(self, display_name, format_name, '/contig/' + format_name + '/overview', 'CONTIG', residues, None, None)
