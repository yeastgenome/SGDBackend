import hashlib

__author__ = 'kpaskov'

from model_new_schema import Base, EqualityByIDMixin
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Numeric, CLOB

class Sequence(Base, EqualityByIDMixin):
    __tablename__ = 'biosequence'

    id = Column('biosequence_id', Integer, primary_key=True)
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
        Sequence.__init__(self, 'Sequence: ' + hash, hash, 'DNA', residues, None, None)

class Rnasequence(Sequence):
    __mapper_args__ = {'polymorphic_identity': "RNA",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, residues):
        hash = hashlib.md5(residues).hexdigest()
        Sequence.__init__(self, 'Sequence: ' + hash, hash, 'RNA', residues, None, None)

class Proteinsequence(Sequence):
    __tablename__ = "proteinbiosequence"

    id = Column('biosequence_id', Integer, ForeignKey(Sequence.id), primary_key=True)
    dnasequence_id = Column('dnasequence_id', Integer)

    __mapper_args__ = {'polymorphic_identity': 'PROTEIN',
                       'inherit_condition': id == Sequence.id}

    def __init__(self, residues, dnasequence, date_created=None, created_by=None):
        hash = hashlib.md5(residues).hexdigest()
        Sequence.__init__(self, 'Sequence: ' + hash, str(dnasequence.id),
                           'PROTEIN', residues, date_created, created_by)
        self.dnasequence_id = dnasequence.id

class Contig(Sequence):
    __mapper_args__ = {'polymorphic_identity': "CONTIG",
                       'inherit_condition': id==Sequence.id}

    def __init__(self, display_name, residues, strain):
        format_name = strain.format_name + '_' + display_name
        Sequence.__init__(self, display_name, format_name, 'CONTIG', residues, None, None)
