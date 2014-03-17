from datetime import timedelta, date

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from src.sgd.backend.nex.obj_to_json import link_gene_names, author_to_json
from src.sgd.backend.nex.query_tools import get_bioentity_references
from src.sgd.model.nex.reference import Bibentry, Abstract, AuthorReference, Author, Reference, Referencerelation, ReferenceReftype
from src.sgd.backend.nex.cache import get_obj
from src.sgd.backend.nex import view_literature, DBSession


__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def make_overview(reference_id):
    reference = dict(get_obj(Reference, reference_id))

    abstracts = DBSession.query(Abstract).filter(Abstract.id == reference_id).all()
    reference['abstract'] = None if len(abstracts) != 1 or abstracts[0] is None else link_gene_names(abstracts[0].text)

    bibentries = DBSession.query(Bibentry).filter(Bibentry.id == reference_id).all()
    reference['bibentry'] = None if len(bibentries) != 1 else bibentries[0].text
    reference['reftypes'] = [x.reftype.display_name for x in DBSession.query(ReferenceReftype).options(joinedload(ReferenceReftype.reftype)).filter(ReferenceReftype.reference_id == reference_id).all()]

    author_refs = DBSession.query(AuthorReference).options(joinedload("author")).filter(AuthorReference.reference_id == reference_id).all()
    author_refs.sort(key=lambda x: x.order)
    reference['authors'] = [author_to_json(author_ref.author) for author_ref in author_refs]

    bioentity_references = get_bioentity_references(reference_id=reference_id)
    reference['counts'] = {'interaction': len([x for x in bioentity_references if x.class_type == 'PHYSINTERACTION' or x.class_type == 'GENINTERACTION']),
                            'go': len([x for x in bioentity_references if x.class_type == 'GO']),
                            'phenotype': len([x for x in bioentity_references if x.class_type == 'PHENOTYPE']),
                            'regulation': len([x for x in bioentity_references if x.class_type == 'REGULATION']),}

    related_refs = DBSession.query(Referencerelation).filter(or_(Referencerelation.parent_id == reference_id, Referencerelation.child_id == reference_id)).all()
    related_references = [get_obj(Reference, x.child_id) for x in related_refs if x.parent_id == reference_id]
    related_references.extend([get_obj(Reference, x.parent_id) for x in related_refs if x.child_id == reference_id])
    for refrel in related_references:
        abstracts = DBSession.query(Abstract).filter(Abstract.id == reference_id).all()
        refrel['abstract'] = None if len(abstracts) != 1 or abstracts[0] is None else link_gene_names(abstracts[0].text)
        refrel['reftypes'] = [x.reftype.display_name for x in DBSession.query(ReferenceReftype).options(joinedload(ReferenceReftype.reftype)).filter(ReferenceReftype.reference_id == refrel['id']).all()]
    reference['related_references'] = related_references

    return reference

# -------------------------------Author---------------------------------------
def make_author(author_identifier):
    try:
        author_id = int(author_identifier)
        query = DBSession.query(Author).filter(Author.id == author_id)
    except:
        query = DBSession.query(Author).filter(Author.format_name == author_identifier)
    author = query.first()
    return None if author is None else author_to_json(author)

def make_author_references(author_id):
    author_refs = DBSession.query(AuthorReference).filter(AuthorReference.author_id == author_id).all()
    references = [get_obj(Reference, author_ref.reference_id) for author_ref in author_refs]
    references.sort(key=lambda x: (x['year'], x['pubmed_id']), reverse=True) 
    return references

# -------------------------------This Week---------------------------------------
def make_references_this_week():
    a_week_ago = date.today() - timedelta(days=7)
    references = DBSession.query(Reference).filter(Reference.date_created > a_week_ago).all()
    references = [get_obj(Reference, x.id) for x in sorted(references, key=lambda x: x.date_created, reverse=True)]
    for reference in references:
        literature_details = view_literature.make_details(reference_id=reference['id'])
        reference['literature_details'] = literature_details
    return references
