from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model.nex import UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Pathway(Dbentity):
    __tablename__ = "pathwaydbentity"

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'PATHWAY', 'inherit_condition': id == Dbentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'dbentity_status',
                     'description', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['sgdid', 'format_name', 'id']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)