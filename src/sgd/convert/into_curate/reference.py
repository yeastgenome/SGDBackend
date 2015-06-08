from src.sgd.convert.into_curate import basic_convert, remove_nones

from sqlalchemy.orm import joinedload
from datetime import datetime

__author__ = 'kpaskov'


def load_urls(bud_reference, pubmed_id, bud_session):
    urls = []

    from src.sgd.model.bud.reference import Ref_URL

    doi = None
    pubmed_central_id = None
    for ref_url in bud_session.query(Ref_URL).options(joinedload('url')).filter_by(reference_id=bud_reference.id).all():
        urls.append({'name': ref_url.url.url_type,
                     'link': ref_url.url.url,
                     'source': {'name': ref_url.url.source},
                     'url_type': ref_url.url.url_type,
                     'bud_id': ref_url.id})

        if ref_url.url.url_type == 'PMC full text':
            pubmed_central_id = ref_url.url.url.replace('http://www.ncbi.nlm.nih.gov/pmc/articles/', '')[:-1]
        elif ref_url.url.url_type == 'DOI full text':
            doi = ref_url.url.url[18:]

    if pubmed_id is not None:
        urls.append({'name': 'PubMed',
                     'link': 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(pubmed_id),
                     'source': {'name': 'PubMed'},
                     'url_type': 'PUBMED'})
    if doi is not None:
        urls.append({'name': 'Full-Text',
                     'link': 'http://dx.doi.org/' + doi,
                     'source': {'name': 'DOI'},
                     'url_type': 'FULLTEXT'})
    if pubmed_central_id is not None:
        urls.append({'name': 'PMC',
                     'link': 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(pubmed_central_id),
                     'source': {'name': 'PubMedCentral'},
                     'url_type': 'PUBMEDCENTRAL'})
    return urls, pubmed_central_id, doi


def load_aliases(bud_reference, bud_session):
    aliases = []

    from src.sgd.model.bud.reference import DbxrefRef

    for ref_dbxref in bud_session.query(DbxrefRef).options(joinedload(DbxrefRef.dbxref)).filter_by(reference_id=bud_reference.id).all():
        aliases.append({'name': ref_dbxref.dbxref.dbxref_id,
                        'source': {'name': 'SGD'},
                        'alias_type': ref_dbxref.dbxref.dbxref_type,
                        'bud_id': ref_dbxref.dbxref.id,
                        'date_created': str(ref_dbxref.dbxref.date_created),
                        'created_by': ref_dbxref.dbxref.created_by})

    return aliases


def load_reftypes(bud_reference, bud_session):
    reftypes = []

    from src.sgd.model.bud.reference import RefReftype

    for old_refreftype in bud_session.query(RefReftype).options(joinedload(RefReftype.reftype)).filter_by(reference_id=bud_reference.id).all():
        reftypes.append({'name': old_refreftype.reftype.name,
                         'source': {'name': old_refreftype.reftype.source}})
    return reftypes


def load_authors(bud_reference, bud_session):
    authors = []

    from src.sgd.model.bud.reference import AuthorReference

    for old_author_reference in bud_session.query(AuthorReference).options(joinedload(AuthorReference.author)).filter_by(reference_id=bud_reference.id).all():
        authors.append({'name': old_author_reference.author.name,
                        'source': {'name': 'PubMed'},
                        'author_order': old_author_reference.order,
                        'author_type': old_author_reference.type})

    return authors


def load_relations(bud_reference, bud_session):
    from src.sgd.model.bud.reference import RefRelation

    relations = []
    for bud_obj in bud_session.query(RefRelation).options(joinedload(RefRelation.child)).filter_by(parent_id=bud_reference.id).all():
        relations.append(remove_nones({
            "sgdid": bud_obj.child.dbxref_id,
            "relation_type": 'None' if bud_obj.description is None else bud_obj.description,
            "date_created": str(bud_obj.date_created),
            "created_by": bud_obj.created_by
        }))
    return relations


def load_documents(bud_reference, bud_session):
    from src.sgd.model.bud.reference import Abstract

    documents = []

    #Abstract
    abstract = bud_session.query(Abstract).filter_by(reference_id=bud_reference.id).first()
    if abstract is not None:
        documents.append(
            {'text': abstract.text,
             'html': abstract.text,
             'source': {'name': 'SGD'},
             'document_type': 'Abstract',
             'date_created': str(bud_reference.date_created),
             'created_by': bud_reference.created_by})
    return documents


def reference_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference

    bud_session = bud_session_maker()

    for old_reference in bud_session.query(Reference).order_by(Reference.id.desc()).options(joinedload('book'), joinedload('journal')).all():
        new_journal = None
        old_journal = old_reference.journal
        if old_journal is not None:
            abbreviation = old_journal.abbreviation
            if old_journal.issn == '0948-5023':
                abbreviation = 'J Mol Model (Online)'
            new_journal = remove_nones({'title': old_journal.full_name,
                                        'med_abbr': abbreviation,
                                        'issn_print': old_journal.issn,
                                        'source': {'name': old_reference.source}})

        new_book = None
        old_book = old_reference.book
        if old_book is not None:
            new_book = remove_nones({'title': old_book.title,
                                     'volume_title': old_book.volume_title,
                                     'publisher_location': old_book.publisher_location,
                                     'isbn': old_book.isbn,
                                     'source': {'name': old_reference.source}})

        pubmed_id = None
        if old_reference.pubmed_id is not None:
            pubmed_id = old_reference.pubmed_id

        year = None
        if old_reference.year is not None:
            year = int(old_reference.year)

        urls, pubmed_central_id, doi = load_urls(old_reference, pubmed_id, bud_session)

        obj_json = remove_nones({'bud_id': old_reference.id,
                    'sgdid': old_reference.dbxref_id,
                    'source': {'name': old_reference.source},
                    'method_obtained': old_reference.status,
                    'dbentity_status': 'Active',
                    'pubmed_id': pubmed_id,
                    'fulltext_status': old_reference.pdf_status,
                    'citation': old_reference.citation.replace('()', ''),
                    'year': year,
                    'date_published': old_reference.date_published,
                    'date_revised': None if old_reference.date_revised is None else str(datetime.strptime(str(old_reference.date_revised), '%Y%m%d').date()),
                    'issue': old_reference.issue,
                    'page': old_reference.page,
                    'volume': old_reference.volume,
                    'title': old_reference.title,
                    'journal': new_journal,
                    'book': new_book,
                    'doi': doi,
                    'pubmed_central_id': pubmed_central_id,
                    'date_created': str(old_reference.date_created),
                    'created_by': old_reference.created_by})

        #Load aliases
        obj_json['aliases'] = load_aliases(old_reference, bud_session)

        #Load urls
        obj_json['urls'] = urls

        #Load reference reftypes
        obj_json['reftypes'] = load_reftypes(old_reference, bud_session)

        #Load reference authors
        obj_json['authors'] = load_authors(old_reference, bud_session)

        #Load children
        obj_json['children'] = load_relations(old_reference, bud_session)

        #Load documents
        obj_json['documents'] = load_documents(old_reference, bud_session)
        obj_json['documents'].append(create_bibentry(obj_json))

        yield obj_json

    bud_session.close()


def create_bibentry(obj_json):
    entries = []
    entries.append(('PMID', obj_json.get('pubmed_id')))
    entries.append(('STAT', obj_json.get('dbentity_status')))
    entries.append(('DP', obj_json.get('date_published')))
    entries.append(('TI', obj_json.get('title')))
    entries.append(('SO', obj_json['source']['name']))
    entries.append(('LR', obj_json.get('date_revised')))
    entries.append(('IP', obj_json.get('issue')))
    entries.append(('PG', obj_json.get('page')))
    entries.append(('VI', obj_json.get('volume')))
    entries.append(('SO', 'SGD'))

    for author in obj_json['authors']:
        entries.append(('AU', author['name']))

    for reftype in obj_json['reftypes']:
        entries.append(('PT', reftype['name']))

    if len(obj_json['documents']) > 0:
        entries.append(('AB', obj_json['documents'][0]['text']))

    if 'journal' in obj_json:
        entries.append(('TA', obj_json['journal'].get('med_abbr')))
        entries.append(('JT', obj_json['journal'].get('title')))
        entries.append(('IS', obj_json['journal'].get('issn_print')))

    if 'book' in obj_json:
        entries.append(('PL', obj_json['book'].get('publisher_location')))
        entries.append(('BTI', obj_json['book'].get('title')))
        entries.append(('VTI', obj_json['book'].get('volume_title')))
        entries.append(('ISBN', obj_json['book'].get('isbn')))


    return {'text': '\n'.join([key + ' - ' + str(value) for key, value in entries if value is not None]),
            'html': '\n'.join([key + ' - ' + str(value) for key, value in entries if value is not None]),
            'source': {'name': 'SGD'},
            'document_type': 'Bibentry'}


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, reference_starter, 'reference', lambda x: x['sgdid'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')