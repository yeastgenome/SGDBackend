from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean, CLOB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin, create_format_name
from src.sgd.model.nex.keyword import Keyword
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.locus import Locus

__author__ = 'kelley, sweng66'

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

    orcid = Column('orcid', String)
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
    postal_code = Column('postal_code', String)
    work_phone = Column('work_phone', String)
    other_phone = Column('other_phone', String)
    # fax = Column('fax', String)
    email = Column('email', String)
    is_pi = Column('is_pi', Boolean)
    is_contact = Column('is_contact', Boolean)
    research_interest = Column('research_interest', String)
    colleague_note = Column('colleague_note', String)
    display_email = Column('display_email', Boolean)
    date_last_modified = Column('date_last_modified', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False, lazy='joined')
    # keywords = association_proxy('colleague_keywords', 'keyword')
    # loci = association_proxy('colleague_loci', 'locus')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'date_created', 
                     'created_by', 'last_name', 'first_name', 'suffix', 'other_last_name', 
                     'profession', 'job_title', 'institution', 'address1', 'address2', 
                     'address3', 'city', 'state', 'country', 'postal_code', 'work_phone',
                     'other_phone', 'email', 'is_pi', 'is_contact', 'display_email', 
                     'research_interest', 'colleague_note', 'date_last_modified']
    __eq_fks__ = [('source', Source, False)]
    #              ('urls', 'colleague.ColleagueUrl', True),
    #              ('associates', 'colleague.ColleagueAssociation', False)]
    __id_values__ = ['format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
    __filter_values__ = ['last_name', 'first_name', 'institution', 'is_pi', 'is_contact']

    def __init__(self, obj_json, session):
        obj_json['link'] = '/colleague/' + self.__create_format_name__(obj_json)
        self.link = obj_json['link']
        UpdateWithJsonMixin.__init__(self, obj_json, session)
        if "is_pi" not in obj_json:
            self.is_pi = False
        if "is_contact" not in obj_json:
            self.is_contact = False
        if "display_email" not in obj_json:
            self.display_email = False

    @classmethod
    def __create_format_name__(cls, obj_json):
        return create_format_name('_'.join([x for x in [obj_json['first_name'], obj_json['last_name'], str(obj_json['bud_id']) ]]))

    @classmethod
    def __create_display_name__(cls, obj_json):
        return obj_json['first_name'] + ' ' + obj_json['last_name']

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)

        #Urls
        # obj_json['urls'] = [x.to_json() for x in sorted(self.urls, key=lambda x: x.display_name)]

        #Relations
        # obj_json['associates'] = [x.to_json() for x in self.associates]
        # obj_json['colleagues'] = [x.to_json() for x in self.colleagues]

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
    # colleague = relationship(Colleague, uselist=False, backref=backref('urls', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'link', 'bud_id', 'url_type',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        self.update(obj_json, session)

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), self.display_name, self.url_type

    @classmethod
    def create_or_find(cls, obj_json, session, colleaguet_obj=None):
        if obj_json is None:
            return None

        newly_created_object = cls(obj_json, session)
        if colleague_obj is not None:
            newly_created_object.colleague_id = colleague_obj.id

        current_obj = session.query(cls)\
            .filter_by(colleague_id=newly_created_object.colleague_id)\
            .filter_by(display_name=newly_created_object.display_name)\
            .filter_by(url_type=newly_created_object.url_type).first()

        if current_obj is None:
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ColleagueAssociation(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_association'

    id = Column('colleague_association_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    associate_id = Column('associate_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    association_type = Column('association_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    # colleague = relationship(Colleague, backref=backref("associates", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[colleague_id])
    # associate = relationship(Colleague, backref=backref("colleagues", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[associate_id])
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'association_type', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    # ('colleague', Colleague, False), ('associate', Colleague, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, colleague_id, associate_id, association_type):
        self.colleague_id = colleague_id
        self.associate_id = associate_id
        self.association_type = association_type

    def unique_key(self):
        return self.colleague_id, self.associate_id, self.association_type
        # (None if self.colleague is None else self.colleague.unique_key()), (None if self.associate is None else self.associate.unique_key(), self.association_type)

    @classmethod
    def create_or_find(cls, obj_json, session, colleague_obj=None):
        if obj_json is None:
            return None

        associate, status = Colleague.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Colleague not found: ' + str(obj_json))

        association_type = obj_json["association_type"]

        current_obj = session.query(cls)\
            .filter_by(colleague_id=colleague_obj.id)\
            .filter_by(associate_id=associate.id)\
            .filter_by(association_type=association_type).first()

        if current_obj is None:
            newly_created_object = cls(colleague_obj, associate, relation_type)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

    #def to_json(self):
    #    obj_json = self.associate.to_min_json()
    #    obj_json['source'] = self.associate.source.to_min_json()
    #    obj_json['association_type'] = self.association_type


class ColleagueKeyword(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_keyword'

    id = Column('colleague_keyword_id', Integer, primary_key=True)
    keyword_id = Column('keyword_id', Integer, ForeignKey(Keyword.id, ondelete='CASCADE'))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    colleague = relationship(Colleague, uselist=False, backref=backref('colleague_keywords', cascade="all, delete-orphan", passive_deletes=True))
    keyword = relationship(Keyword, uselist=False, backref=backref('colleague_keywords', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False), ('keyword', Keyword, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, colleague, keyword):
        self.keyword = keyword
        self.colleague = colleague
        self.source = self.keyword.source

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), (None if self.keyword is None else self.keyword.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, colleague_obj=None):
        if obj_json is None:
            return None

        keyword, status = Keyword.create_or_find(obj_json, session)
        #if status == 'Created':
        #    raise Exception('Keyword not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(colleague_id=colleague_obj.id)\
            .filter_by(keyword_id=keyword.id).first()

        if current_obj is None:
            newly_created_object = cls(colleague_obj, keyword)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'


class ColleagueLocus(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'colleague_locus'

    id = Column('colleague_locus_id', Integer, primary_key=True)
    locus_id = Column('locus_id', Integer, ForeignKey(Locus.id, ondelete='CASCADE'))
    colleague_id = Column('colleague_id', Integer, ForeignKey(Colleague.id, ondelete='CASCADE'))
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    colleague = relationship(Colleague, uselist=False, backref=backref('colleague_loci', cascade="all, delete-orphan", passive_deletes=True))
    locus = relationship(Locus, uselist=False, backref=backref('colleague_loci', cascade="all, delete-orphan", passive_deletes=True))
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False), ('colleague', Colleague, False), ('locus', Locus, False)]
    __id_values__ = []
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, colleague, locus):
        self.locus = locus
        self.colleague = colleague
        self.source = self.locus.source

    def unique_key(self):
        return (None if self.colleague is None else self.colleague.unique_key()), (None if self.locus is None else self.locus.unique_key())

    @classmethod
    def create_or_find(cls, obj_json, session, colleague_obj=None):
        if obj_json is None:
            return None

        locus, status = Locus.create_or_find(obj_json, session)
        if status == 'Created':
            raise Exception('Locus not found: ' + str(obj_json))

        current_obj = session.query(cls)\
            .filter_by(colleague_id=colleague_obj.id)\
            .filter_by(locus_id=locus.id).first()

        if current_obj is None:
            newly_created_object = cls(colleague_obj, locus)
            return newly_created_object, 'Created'
        else:
            return current_obj, 'Found'

