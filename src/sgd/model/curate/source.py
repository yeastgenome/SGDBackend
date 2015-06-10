from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.curate import Base, ToJsonMixin, UpdateWithJsonMixin

__author__ = 'kelley'

class Source(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'source'

    id = Column('source_id', String, primary_key=True)
    name = Column('name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __eq_values__ = ['id', 'name', 'link', 'description', 'bud_id', 'date_created', 'created_by']
    __eq_fks__ = []
    __id_values__ = ['id', 'name']
    __no_edit_values__ = ['id', 'link', 'date_created', 'created_by']
    __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    @classmethod
    def __create_name__(cls, obj_json):
        if obj_json['name'] in to_change:
            return to_change[obj_json['name']]
        else:
            return obj_json['name']

    @classmethod
    def __create_link__(cls, obj_json):
        return None

to_change = {
    'Colleague submission': 'Colleague',
    'Curator': 'SGD',
    'Curator non-PubMed reference': 'SGD',
    'Curator PubMed reference': 'SGD',
    'Curator Triage': 'SGD',
    'FLYBASE': 'FlyBase',
    'GO Consortium': 'GOC',
    'MRC': 'SUPERFAMILY',
    'NCBI protein name': 'NCBI',
    'Non-uniform': 'SGD',
    'Protein Data Bank': 'PDB',
    'PDB script': 'PDB',
    'PubMed script': 'PubMed',
    'Retired name': 'SGD',
    'S. pombe GeneDB': 'PomBase',
    'Transferred from SacchDB': 'SacchDB',
    'Uniform': 'SGD',
    'WB': 'WormBase'
}
