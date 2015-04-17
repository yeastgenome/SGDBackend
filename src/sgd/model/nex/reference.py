from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.journal import Journal
from src.sgd.model.nex.book import Book
from src.sgd.model.nex.reftype import Reftype

__author__ = 'kpaskov'

class Reference(Dbentity):
    __tablename__ = 'referencedbentity'

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)
    method_obtained = Column('method_obtained', String)
    fulltext_status = Column('fulltext_status', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    pubmed_id = Column('pubmed_id', Integer)
    pubmed_central_id = Column('pubmed_central_id', String)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', Date)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer, ForeignKey(Journal.id))
    book_id = Column('book_id', Integer, ForeignKey(Book.id))
    doi = Column('doi', String)

    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)

    author_names = association_proxy('author_references', 'author_name')
    related_references = association_proxy('refrels', 'child_ref')
    reftypes = association_proxy('reference_reftypes', 'reftype')

    __mapper_args__ = {'polymorphic_identity': 'REFERENCE', 'inherit_condition': id == Dbentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'description',
                     'bud_id', 'sgdid', 'dbentity_status', 'date_created', 'created_by',
                     'method_obtained', 'fulltext_status', 'citation', 'year', 'pubmed_id', 'pubmed_central_id', 'date_published', 'date_revised',
                     'issue', 'page', 'volume', 'title', 'doi']
    __eq_fks__ = [('source', Source, False), ('journal', Journal, False), ('book', Book, False),
                  ('aliases', 'reference.ReferenceAlias', True), ('urls', 'reference.ReferenceUrl', True),
                  ('reference_reftypes', 'reference.ReferenceReftype', False)]
    __id_values__ = ['format_name', 'id', 'sgdid', 'pubmed_id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_format_name__(cls, obj_json):
        return create_format_name(obj_json['citation'][0:100])

    @classmethod
    def __create_display_name__(cls, obj_json):
        citation = obj_json['citation']
        return citation[:citation.find(")")+1]

    def to_min_json(self, include_description=False):
        obj_json = ToJsonMixin.to_min_json(self, include_description=include_description)
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['year'] = self.year
        return obj_json

    def to_semi_json(self):
        obj_json = self.to_min_json()
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['citation'] = self.citation
        obj_json['year'] = self.year
        obj_json['journal'] = None if self.journal is None else self.journal.med_abbr
        obj_json['urls'] = [x.to_json() for x in self.urls]
        return obj_json

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['abstract'] = None if len(self.paragraphs) == 0 else self.paragraphs[0].to_json(linkit=True)
        obj_json['bibentry'] = None if self.bibentry is None else self.bibentry.text
        obj_json['reftypes'] = [x.reftype.to_min_json() for x in self.reftypes]
        obj_json['authors'] = [x.author.to_min_json() for x in self.author_references]
        interaction_locus_ids = set()
        interaction_locus_ids.update([x.locus1_id for x in self.physinteraction_evidences])
        interaction_locus_ids.update([x.locus2_id for x in self.physinteraction_evidences])
        interaction_locus_ids.update([x.locus1_id for x in self.geninteraction_evidences])
        interaction_locus_ids.update([x.locus2_id for x in self.geninteraction_evidences])
        regulation_locus_ids = set()
        regulation_locus_ids.update([x.locus1_id for x in self.regulation_evidences])
        regulation_locus_ids.update([x.locus2_id for x in self.regulation_evidences])
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        obj_json['counts'] = {
            'interaction': len(interaction_locus_ids),
            'go': len(set([x.locus_id for x in self.go_evidences])),
            'phenotype': len(set([x.locus_id for x in self.phenotype_evidences])),
            'regulation': len(regulation_locus_ids)
        }
        obj_json['related_references'] = []
        for child in self.children:
            child_json = child.child.to_semi_json()
            child_json['abstract'] = None if len(child.child.paragraphs) == 0 else child.child.paragraphs[0].to_json(linkit=True)
            child_json['reftypes'] = [x.reftype.to_min_json() for x in child.child.reftypes]
            obj_json['related_references'].append(child_json)
        for parent in self.parents:
            parent_json = parent.parent.to_semi_json()
            parent_json['abstract'] = None if len(parent.parent.paragraphs) == 0 else parent.parent.paragraphs[0].to_json(linkit=True)
            parent_json['reftypes'] = [x.reftype.to_min_json() for x in parent.parent.reftypes]
            obj_json['related_references'].append(parent_json)
        obj_json['urls'] = [x.to_json() for x in self.urls]
        if self.journal is not None:
            obj_json['journal']['med_abbr'] = self.journal.med_abbr

        id_to_dataset = {}
        for expression_evidence in self.expression_evidences:
            if expression_evidence.datasetcolumn.dataset_id not in id_to_dataset:
                id_to_dataset[expression_evidence.datasetcolumn.dataset_id] = expression_evidence.datasetcolumn.dataset
        obj_json['expression_datasets'] = [x.to_semi_json() for x in id_to_dataset.values()]
        return obj_json

class ReferenceUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('reference', Reference, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), self.display_name, self.link

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.reference_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(reference_id=newly_created_object.reference_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(link=newly_created_object.link).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

class ReferenceAlias(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    alias_type = Column('alias_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('aliases', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'alias_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('reference', Reference, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), self.display_name, self.alias_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.reference_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(reference_id=newly_created_object.reference_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(alias_type=newly_created_object.alias_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ReferenceRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    parent_id = Column('parent_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Reference, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Reference, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'bud_id', 'relation_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('parent', Reference, False), ('child', Reference, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return self.relation_type, self.parent.unique_key(), self.child.unique_key()

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            if newly_created_object.parent is None:
                newly_created_object.parent_id = parent_obj.id
            elif newly_created_object.child is None:
                newly_created_object.child_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(parent_id=newly_created_object.parent_id)\
            .filter_by(child_id=newly_created_object.child_id)\
            .filter_by(relation_type=newly_created_object.relation_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ReferenceReftype(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'reference_reftype'

    id = Column('reference_reftype_id', Integer, primary_key=True)
    reference_id = Column('reference_id', Integer, ForeignKey(Reference.id, ondelete='CASCADE'))
    reftype_id = Column('reftype_id', Integer, ForeignKey(Reftype.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    reference = relationship(Reference, uselist=False, backref=backref('reference_reftypes', cascade="all, delete-orphan", passive_deletes=True))
    reftype = relationship(Reftype, uselist=False, backref=backref('reference_reftypes', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('reference', Reference, False), ('reftype', Reftype, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, reference, reftype):
        self.reftype = reftype
        self.reference = reference
        self.source_id = self.reftype.source_id

    def unique_key(self):
        return (None if self.reference is None else self.reference.unique_key()), (None if self.reftype is None else self.reftype.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        reftype, status = Reftype.create_or_find(obj_json, session)

        #if status == 'Created':
        #    raise Exception('Keyword not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(reference_id=parent_obj.id)\
            .filter_by(reftype_id=reftype.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, reftype)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'