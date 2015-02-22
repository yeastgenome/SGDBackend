from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model.nex import UpdateWithJsonMixin
from src.sgd.model.nex.dbentity import Dbentity
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class Pathway(Dbentity):
    __tablename__ = "pathwaydbentity"

    id = Column('dbentity_id', Integer, ForeignKey(Dbentity.id), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'PATHWAY', 'inherit_condition': id == Dbentity.id}
    __eq_values__ = ['id', 'display_name', 'format_name', 'class_type', 'link', 'sgdid', 'uniprotid', 'dbent_status',
                     'description', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['sgdid', 'format_name', 'id']

    def __init__(self, obj_json):
        UpdateWithJsonMixin.__init__(self, obj_json)
        self.link = '/pathway/' + self.sgdid
        self.format_name = create_format_name(self.display_name)