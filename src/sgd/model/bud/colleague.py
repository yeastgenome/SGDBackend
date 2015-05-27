from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base
from feature import Feature
from general import Dbxref, Url


class Colleague(Base, EqualityByIDMixin):
    __tablename__ = 'colleague'

    id = Column('colleague_no', Integer, primary_key = True)
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
    address4 = Column('address4', String)
    address5 = Column('address5', String)
    city = Column('city', String)
    state = Column('state', String)
    region = Column('region', String)
    country = Column('country', String)
    postal_code = Column('postal_code', String)
    work_phone = Column('work_phone', String)
    other_phone = Column('other_phone', String)
    fax = Column('fax', String)
    email = Column('email', String)
    source = Column('source', String)
    is_pi = Column('is_pi', String)
    is_contact = Column('is_contact', String)
    display_email = Column('display_email', String)
    date_last_modified = Column('date_modified', Date)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

class ColleagueUrl(Base):
    __tablename__ = 'coll_url'

    id = Column('coll_url_no', Integer, primary_key = True)
    colleague_id = Column('colleague_no', Integer, ForeignKey(Colleague.id))
    url_id = Column('url_no', Integer, ForeignKey(Url.id))

    url = relationship(Url, uselist=False)
    reference = relationship(Colleague, uselist=False)

class ColleagueRelation(Base):
    __tablename__ = 'coll_relationship'

    id = Column('coll_relationship_no', Integer, primary_key=True)
    colleague_id = Column('colleague_no', Integer, ForeignKey(Colleague.id))
    associate_id = Column('associate_no', Integer, ForeignKey(Colleague.id))
    relationship_type = Column('relationship_type', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    colleague = relationship(Colleague, backref=backref("associates", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[colleague_id])
    associate = relationship(Colleague, backref=backref("colleagues", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[associate_id])

class ColleagueFeature(Base):
    __tablename__ = 'coll_feat'

    id = Column('coll_feat_no', Integer, primary_key=True)
    colleague_id = Column('colleague_no', Integer, ForeignKey(Colleague.id))
    feature_id = Column('feature_no', Integer, ForeignKey(Feature.id))

    colleague = relationship(Colleague, uselist=False)
    feature = relationship(Feature, uselist=False)

class Keyword(Base):
    __tablename__ = 'keyword'

    id = Column('keyword_no', Integer, primary_key=True)
    keyword = Column('keyword', String)
    source = Column('source', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

class ColleagueKeyword(Base):
    __tablename__ = 'coll_kw'

    id = Column('coll_kw_no', Integer, primary_key=True)
    colleague_id = Column('colleague_no', Integer, ForeignKey(Colleague.id))
    feature_id = Column('keyword_no', Integer, ForeignKey(Keyword.id))

    colleague = relationship(Colleague, uselist=False)
    keyword = relationship(Keyword, uselist=False)

class ColleagueRemark(Base):
    __tablename__ = 'colleague_remark'

    id = Column('colleague_remark_no', Integer, primary_key=True)
    colleague_id = Column('colleague_no', Integer, ForeignKey(Colleague.id))
    remark = Column('remark', String)
    remark_type = Column('remark_type', String)
    remark_date = Column('remark_date', Date)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)


    colleague = relationship(Colleague, uselist=False)
