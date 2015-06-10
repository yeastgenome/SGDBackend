from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Date, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import ToJsonMixin, UpdateWithJsonMixin, Base
from src.sgd.model.curate.source import Source
from src.sgd.model.curate.taxonomy import Taxonomy
from src.sgd.model.curate.dbentity import Dbentity
from src.sgd.model.curate.reference import Reference

__author__ = 'kelley'

class Strain(Dbentity):
    __tablename__ = 'straindbentity'

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)
    taxonomy_id = Column('taxonomy_id', String, ForeignKey(Taxonomy.id))
    strain_type = Column('strain_type', String)
    genotype = Column('genotype', String)
    genbank_id = Column('genbank_id', String)
    assembly_size = Column('assembly_size', Integer)
    fold_coverage = Column('fold_coverage', Integer)
    scaffold_number = Column('scaffold_number', Integer)
    longest_scaffold = Column('longest_scaffold', Integer)
    scaffold_nfifty = Column('scaffold_nfifty', Integer)

    #Relationships
    taxonomy = relationship(Taxonomy, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'STRAIN', 'inherit_condition': id == Dbentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description', 'bud_id', 'date_created', 'created_by', 'sgdid', 'dbentity_status',
                     'strain_type', 'genotype', 'genbank_id', 'assembly_size', 'fold_coverage', 'scaffold_number', 'longest_scaffold', 'scaffold_nfifty']
    __eq_fks__ = [('source', Source, False),
                  ('taxonomy', Taxonomy, False),
                  ('urls', 'strain.StrainUrl', True),
                  ('documents', 'strain.StrainDocument', True)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['strain_type']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        #obj_json['contigs'] = [contig.to_semi_json() for contig in self.contigs]
        return obj_json


class StrainUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'strain_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    strain = relationship(Strain, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('strain', Strain, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.strain is None else self.strain.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.strain_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(strain_id=newly_created_object.strain_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

class StrainDocument(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'strain_document'

    id = Column('document_id', Integer, primary_key=True)
    document_type = Column('document_type', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    strain_id = Column('strain_id', Integer, ForeignKey(Strain.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    strain = relationship(Strain, uselist=False, backref=backref('documents', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'document_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('strain', Strain, False),
                  ('references', 'strain.StrainDocumentReference', False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.strain is None else self.strain.unique_key()), self.document_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.strain_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(strain_id=newly_created_object.strain_id)\
            .filter_by(document_type=newly_created_object.document_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class StrainDocumentReference(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'strain_document_reference'

    id = Column('document_reference_id', Integer, primary_key=True)
    document_id = Column('document_id', Integer, ForeignKey(StrainDocument.id, ondelete='CASCADE'))
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    reference_order = Column('reference_order', Integer)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    document = relationship(StrainDocument, uselist=False, backref=backref('references', cascade="all, delete-orphan", passive_deletes=True))
    reference = relationship(Reference, uselist=False, backref=backref('strain_documents', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'reference_order', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False),
                  ('document', StrainDocument, False),
                  ('reference', Reference, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, document, reference, reference_order):
        self.reference_order = reference_order
        self.document = document
        self.reference_id = reference.id
        self.source = self.document.source

    def unique_key(self):
        return (None if self.document is None else self.document.unique_key()), (None if self.reference is None else self.reference.unique_key())

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