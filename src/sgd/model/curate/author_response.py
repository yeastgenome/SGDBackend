from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB, Boolean
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin, UpdateWithJsonMixin, create_format_name
from src.sgd.model.nex.source import Source

__author__ = 'kelley'

class AuthorResponse(Base, EqualityByIDMixin, ToJsonMixin, UpdateWithJsonMixin):
    __tablename__ = 'author_response'

    id = Column('author_response_id', Integer, primary_key=True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)
    pubmed_id = Column('pubmed_id', Integer)
    citation = Column('citation', String)
    author_email = Column('author_email', String)
    has_novel_research = Column('has_novel_research', Boolean)
    has_large_scale_data = Column('has_large_scale_data', Boolean)
    research_results = Column('research_results', CLOB)
    gene_list = Column('gene_list', String)
    dataset_description = Column('dataset_description', String)
    other_description = Column('other_description', String)
    no_action_required = Column('no_action_required', Boolean)
    is_fast_tracked = Column('is_fast_tracked', Boolean)
    curator_checked_datasets = Column('curator_checked_datasets', Boolean)
    curator_checked_genelist = Column('curator_checked_genelist', Boolean)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    #Relationships
    source = relationship(Source, uselist=False)

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'source_id', 'bud_id',
                     'pubmed_id', 'citation', 'author_email', 'has_novel_research', 'has_large_scale_data', 'research_results', 'gene_list', 'dataset_description',
                     'other_description', 'no_action_required', 'is_fast_tracked', 'curator_checked_datasets', 'curator_checked_genelist',
                     'date_created', 'created_by']
    __eq_fks__ = [('source', Source, False)]
    __id_values__ = ['id', 'format_name']
    __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)
        self.display_name = self.citation

    def unique_key(self):
        return self.citation

    def __create_format_name__(self):
        return self.citation[0:100]

    def __create_link__(self):
        return '/author_response/' + self.format_name

