from datetime import timedelta, date

from src.sgd.model.nex.reference import AuthorReference, Reference
from src.sgd.backend.nex import view_literature, DBSession

__author__ = 'kpaskov'

# -------------------------------Author---------------------------------------
def make_author_references(author_id):
    references = [x.reference.to_semi_full_json() for x in DBSession.query(AuthorReference).filter(AuthorReference.author_id == author_id).all()]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references

# -------------------------------This Week---------------------------------------
def make_references_this_week():
    a_week_ago = date.today() - timedelta(days=7)
    references = [x.to_json() for x in sorted(DBSession.query(Reference).filter(Reference.date_created > a_week_ago).all(), key=lambda x: x.date_created, reverse=True)]
    for reference in references:
        literature_details = view_literature.make_details(reference_id=reference['id'])
        reference['literature_details'] = literature_details
    return references
