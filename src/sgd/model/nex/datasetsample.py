from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, Boolean
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, UpdateWithJsonMixin, ToJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.dataset import Dataset

__author__ = 'sweng66'

class Datasetsample(Base, EqualityByIDMixin, UpdateWithJsonMixin, ToJsonMixin):
    __tablename__ = 'datasetsample'

    id = Column('datasetsample_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    dataset_id = Column('dataset_id', Integer, ForeignKey(Dataset.id, ondelete='CASCADE'))
    dbxref_id = Column('dbxref_id', String)
    dbxref_type = Column('dbxref_type', String)
    sample_order = Column('sample_order', Integer)
    description = Column('description', String)
    biosample = Column('biosample', String)
    strain_name = Column('strain_name', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)
    
    __eq_values__ = ['id', 'format_name', 'display_name', 'link', 'bud_id', 'dataset_id', 
                     'dbxref_id', 'dbxref_type', 'sample_order', 'description', 'biosample', 
                     'strain_name', 'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.lab_name, self.lab_location, self.dataset_id

        

