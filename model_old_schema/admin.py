'''
Created on Nov 9, 2012

@author: kpaskov
'''
from model_old_schema import current_user, Base
from model_old_schema.config import SCHEMA
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
import datetime

class RefCuration(Base):
    __tablename__ = 'ref_curation'
    __table_args__ = {'schema': SCHEMA, 'extend_existing':True}

    id = Column('ref_curation_no', Integer, primary_key = True)
    reference_id = Column('reference_no', Integer, ForeignKey('bud.reference.reference_no'))
    task = Column('curation_task', String)
    feature_id = Column('feature_no', Integer, ForeignKey('bud.feature.feature_no'))
    comment = Column('curator_comment', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)

    def __init__(self, reference_id, task, feature_id):
        self.reference_id = reference_id
        self.task = task
        self.feature_id = feature_id
        self.created_by = current_user
        self.date_created = datetime.datetime.now()

    def __repr__(self):
        data = self.task, self.feature_id, self.comment
        return 'RefCuration(task=%s, feature_id=%s, comment=%s)' % data