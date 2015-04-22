from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin, create_format_name
from src.sgd.model.nex.keyword import Keyword
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus

__author__ = 'kelley'

class Colleague(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = "colleague"

    id = Column('colleague_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    last_name = Column('last_name', String)
    first_name = Column('first_name', String)
    suffix = Column('suffix', String)
    other_last_name = Column('other_last_name', String)
    profession = Column('profession', String)
    job_title = Column('job_title', String)
    institution = Column('institution', String)
    address1 = Column('address1', String)
    address2 = Column('address2', String)
    address3 = Column('address3', String)
    city = Column('city', String)
    state = Column('state', String)
    country = Column('country', String)
    work_phone = Column('work_phone', String)
    other_phone = Column('other_phone', String)
    fax = Column('fax', String)
    email = Column('email', String)
    is_pi = Column('is_pi', Boolean)
    is_contact = Column('is_contact', Boolean)
    display_email = Column('display_email', Boolean)
    date_last_modified = Column('date_last_modified', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    keywords = association_proxy('colleague_keywords', 'keyword')
    loci = association_proxy('colleague_locuses', 'locus')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'date_created', 'created_by',
                     'last_name', 'first_name', 'suffix', 'other_last_name', 'profession', 'job_title',
                     'institution', 'address1', 'address2', 'address3', 'city', 'state', 'country', 'work_phone',
                     'other_phone', 'fax', 'email', 'is_pi', 'is_contact', 'display_email', 'date_last_modified']
    __eq_fks__ = [('source', Source, False),
                  ('urls', 'colleague.ColleagueUrl', True),
                  ('documents', 'colleague.ColleagueDocument', True),
                  ('colleague_locuses', 'colleague.ColleagueLocus', False),
                  ('colleague_keywords', 'colleague.ColleagueKeyword', False),
                  ('children', 'colleague.ColleagueRelation', False)]
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)
        if "is_pi" not in obj_json:
            self.is_pi = False
        if "is_contact" not in obj_json:
            self.is_contact = False
        if "display_email" not in obj_json:
            self.display_name = False

    @classmethod
    def __create_format_name__(cls, obj_json):
        return create_format_name('_'.join([x for x in [obj_json['first_name'], obj_json['last_name'], None if 'institution' not in obj_json else obj_json['institution']] if x is not None])[0:100])

    @classmethod
    def __create_display_name__(cls, obj_json):
        return obj_json['first_name'] + ' ' + obj_json['last_name']

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)

        #Urls
        obj_json['urls'] = [x.to_json() for x in sorted(self.urls, key=lambda x: x.display_name)]

        #Relations
        obj_json['children'] = [x.to_json() for x in self.children]
        obj_json['parents'] = [x.to_json() for x in self.parents]

        #Keywords
        obj_json['colleague_keywords'] = [x.to_min_json() for x in self.keywords]

        #Loci
        obj_json['colleague_locuses'] = [x.to_min_json() for x in self.loci]

        return obj_json

    def to_min_json(self, include_description=False):
        obj_json = ToJsonMixin.to_min_json(self, include_description)
        obj_json['first_name'] = self.first_name
        obj_json['last_name'] = self.last_name
        obj_json['institution'] = self.institution
        return obj_json


class ColleagueUrl(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_url'

    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    url_type = Column('url_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    colleague = relationship(Colleague, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), self.display_name, self.url_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.colleague_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(colleague_id=newly_created_object.colleague_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(url_type=newly_created_object.url_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ColleagueRelation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_relation'

    id = Column('relation_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    parent_id = Column('parent_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    child_id = Column('child_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    parent = relationship(Colleague, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Colleague, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'relation_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('parent', Colleague, False), ('child', Colleague, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, parent, child, relation_type):
        self.parent = parent
        self.child = child
        self.source = self.child.source
        self.relation_type = relation_type

    def unique_key(self):
        return (None if self.parent is None else self.parent.unique_key()), (None if self.child is None else self.child.unique_key(), self.relation_type)

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        child, status = Colleague.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Colleague not found: ' + str(obj_json))

        relation_type = obj_json["relation_type"]

        current_obj = session.query(cls)\
            .filter_by(parent_id=parent_obj.id)\
            .filter_by(child_id=child.id)\
            .filter_by(relation_type=relation_type).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, child, relation_type)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    def to_json(self):
        obj_json = self.child.to_min_json()
        obj_json['source'] = self.child.source.to_min_json()
        obj_json['relation_type'] = self.relation_type


class ColleagueDocument(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_document'

    id = Column('document_id', Integer, primary_key=True)
    document_type = Column('document_type', String)
    text = Column('text', CLOB)
    html = Column('html', CLOB)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    colleague = relationship(Colleague, uselist=False, backref=backref('documents', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'text', 'html', 'bud_id', 'document_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), self.document_type

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if parent_obj is not None:
            newly_created_object.colleague_id = parent_obj.id

        current_obj = session.query(cls)\
            .filter_by(colleague_id=newly_created_object.colleague_id)\
            .filter_by(document_type=newly_created_object.document_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

class ColleagueKeyword(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_keyword'

    id = Column('colleague_keyword_id', Integer, primary_key=True)
    keyword_id = Column('keyword_id', Integer, ForeignKey(Keyword.id, ondelete='CASCADE'))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    colleague = relationship(Colleague, uselist=False, backref=backref('colleague_keywords', cascade="all, delete-orphan", passive_deletes=True))
    keyword = relationship(Keyword, uselist=False, backref=backref('colleague_keywords', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False), ('keyword', Keyword, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, colleague, keyword):
        self.keyword = keyword
        self.colleague = colleague
        self.source = self.keyword.source

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), (None if self.keyword is None else self.keyword.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        keyword, status = Keyword.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Keyword not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(colleague_id=parent_obj.id)\
            .filter_by(keyword_id=keyword.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, keyword)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ColleagueLocus(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_locus'

    id = Column('colleague_locus_id', Integer, primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id, ondelete='CASCADE'))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    colleague = relationship(Colleague, uselist=False, backref=backref('colleague_locuses', cascade="all, delete-orphan", passive_deletes=True))
    locus = relationship(Locus, uselist=False, backref=backref('colleague_locuses', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False), ('locus', Locus, False)]
    __id_values__ = ['format_name']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, colleague, locus):
        self.locus = locus
        self.colleague = colleague
        self.source = self.locus.source

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), (None if self.locus is None else self.locus.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        locus, status = Locus.create_or_find(obj_json, session)
        if status == 'Created':
            raise Exception('Locus not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(colleague_id=parent_obj.id)\
            .filter_by(locus_id=locus.id).first()

        if current_obj is None:
            newly_created_object = cls(parent_obj, locus)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

