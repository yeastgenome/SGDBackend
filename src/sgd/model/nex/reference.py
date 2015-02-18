from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date, CLOB

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, ToJsonMixin
from src.sgd.model.nex.source import Source
from src.sgd.model.nex.journal import Journal
from src.sgd.model.nex.book import Book

__author__ = 'kpaskov'

class Reference(Base, EqualityByIDMixin, ToJsonMixin):
    __tablename__ = 'reference'

    id = Column('reference_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    sgdid = Column('sgdid', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    bud_id = Column('bud_id', Integer)

    ref_status = Column('ref_status', String)
    pubmed_id = Column('pubmed_id', Integer)
    pubmed_central_id = Column('pubmed_central_id', String)
    fulltext_status = Column('fulltext_status', String)
    citation = Column('citation', String)
    year = Column('year', Integer)
    date_published = Column('date_published', String)
    date_revised = Column('date_revised', String)
    issue = Column('issue', String)
    page = Column('page', String)
    volume = Column('volume', String)
    title = Column('title', String)
    journal_id = Column('journal_id', Integer, ForeignKey(Journal.id))
    book_id = Column('book_id', Integer, ForeignKey(Book.id))
    doi = Column('doi', String)
    created_by = Column('created_by', String, server_default=FetchedValue())
    date_created = Column('date_created', Date, server_default=FetchedValue())

    book = relationship(Book, uselist=False)
    journal = relationship(Journal, uselist=False)
    source = relationship(Source, uselist=False, lazy='joined')

    author_names = association_proxy('author_references', 'author_name')
    related_references = association_proxy('refrels', 'child_ref')

    __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'sgdid', 'ref_status', 'pubmed_id',
                     'pubmed_central_id', 'fulltext_status', 'citation', 'year', 'date_published', 'date_revised',
                     'issue', 'page', 'volume', 'title', 'doi', 'bud_id',
                     'date_created', 'created_by']
    __eq_fks__ = ['source', 'journal', 'book']
    __id_values__ = ['format_name', 'id', 'sgdid', 'pubmed_id']

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.display_name = citation[:citation.find(")")+1]
        self.format_name = self.sgdid if self.pubmed_id is None else str(self.pubmed_id)
        self.link = '/reference/' + self.sgdid

    def unique_key(self):
        return self.format_name

    def to_min_json(self, include_description=False):
        obj_json = UpdateByJsonMixin.to_min_json(self, include_description=include_description)
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['year'] = self.year
        return obj_json

    def to_semi_json(self):
        obj_json = self.to_min_json()
        obj_json['pubmed_id'] = self.pubmed_id
        obj_json['citation'] = self.citation
        obj_json['year'] = self.year
        obj_json['journal'] = None if self.journal is None else self.journal.med_abbr
        obj_json['urls'] = [x.to_json() for x in self.urls]
        return obj_json

    def to_full_json(self):
        obj_json = self.to_json()
        obj_json['abstract'] = None if len(self.paragraphs) == 0 else self.paragraphs[0].to_json(linkit=True)
        obj_json['bibentry'] = None if self.bibentry is None else self.bibentry.text
        obj_json['reftypes'] = [x.reftype.to_min_json() for x in self.ref_reftypes]
        obj_json['authors'] = [x.author.to_min_json() for x in self.author_references]
        interaction_locus_ids = set()
        interaction_locus_ids.update([x.locus1_id for x in self.physinteraction_evidences])
        interaction_locus_ids.update([x.locus2_id for x in self.physinteraction_evidences])
        interaction_locus_ids.update([x.locus1_id for x in self.geninteraction_evidences])
        interaction_locus_ids.update([x.locus2_id for x in self.geninteraction_evidences])
        regulation_locus_ids = set()
        regulation_locus_ids.update([x.locus1_id for x in self.regulation_evidences])
        regulation_locus_ids.update([x.locus2_id for x in self.regulation_evidences])
        obj_json['urls'] = [x.to_min_json() for x in self.urls]
        obj_json['counts'] = {
            'interaction': len(interaction_locus_ids),
            'go': len(set([x.locus_id for x in self.go_evidences])),
            'phenotype': len(set([x.locus_id for x in self.phenotype_evidences])),
            'regulation': len(regulation_locus_ids)
        }
        obj_json['related_references'] = []
        for child in self.children:
            child_json = child.child.to_semi_json()
            child_json['abstract'] = None if len(child.child.paragraphs) == 0 else child.child.paragraphs[0].to_json(linkit=True)
            child_json['reftypes'] = [x.reftype.to_min_json() for x in child.child.ref_reftypes]
            obj_json['related_references'].append(child_json)
        for parent in self.parents:
            parent_json = parent.parent.to_semi_json()
            parent_json['abstract'] = None if len(parent.parent.paragraphs) == 0 else parent.parent.paragraphs[0].to_json(linkit=True)
            parent_json['reftypes'] = [x.reftype.to_min_json() for x in parent.parent.ref_reftypes]
            obj_json['related_references'].append(parent_json)
        obj_json['urls'] = [x.to_json() for x in self.urls]
        if self.journal is not None:
            obj_json['journal']['med_abbr'] = self.journal.med_abbr

        id_to_dataset = {}
        for expression_evidence in self.expression_evidences:
            if expression_evidence.datasetcolumn.dataset_id not in id_to_dataset:
                id_to_dataset[expression_evidence.datasetcolumn.dataset_id] = expression_evidence.datasetcolumn.dataset
        obj_json['expression_datasets'] = [x.to_semi_json() for x in id_to_dataset.values()]
        return obj_json