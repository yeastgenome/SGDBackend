from datetime import timedelta, date

from src.sgd.model.nex.reference import AuthorReference, Reference
from src.sgd.backend.nex import DBSession

__author__ = 'kpaskov'

# -------------------------------Author---------------------------------------
def make_author_references(author_id):
    return [x.reference.to_semi_full_json() for x in sorted(DBSession.query(AuthorReference).filter(AuthorReference.author_id == author_id).all(), key=lambda x: (x.year, x.pubmed_id), reverse=True)]

# -------------------------------This Week---------------------------------------
def make_references_this_week():
    a_week_ago = date.today() - timedelta(days=7)
    return [x.to_semi_full_json() for x in sorted(DBSession.query(Reference).filter(Reference.date_created > a_week_ago).all(), key=lambda x: x.date_created, reverse=True)]
