from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class AuthorResponse(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'author_response'

    id = Column('author_response_id', Integer, primary_key=True)
    pubmed_id = Column('pubmed_id', Integer)
    citation = Column('citation', String)
    author_email = Column('author_email', String)
    has_novel_research = Column('has_novel_research', Integer)
    has_large_scale_data = Column('has_large_scale_data', Integer)
    research_results = Column('research_results', CLOB)
    gene_list = Column('gene_list', String)
    dataset_description = Column('dataset_description', String)
    other_description = Column('other_description', String)
    no_action_requred = Column('no_action_requred', Integer)
    is_fast_tracked = Column('is_fast_tracked', Integer)
    curator_checked_datasets = Column('curator_checked_datasets', Integer)
    curator_checked_genelist = Column('curator_checked_genelist', Integer)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    __eq_values__ = ['id', 'pubmed_id', 'citation', 'author_email', 'has_novel_research', 'has_large_scale_data', 'research_results', 'gene_list', 'dataset_description',
                     'other_description', 'no_action_requred', 'is_fast_tracked', 'curator_checked_datasets', 'curator_checked_genelist',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id']
    __no_edit_values__ = ['id', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def unique_key(self):
        return self.citation

    def __create_format_name__(self):
        return self.citation
