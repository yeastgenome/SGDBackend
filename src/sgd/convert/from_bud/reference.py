from src.sgd.convert.from_bud import basic_convert, remove_nones

from sqlalchemy.orm import joinedload
from datetime import datetime

__author__ = 'kpaskov'


def load_urls(bud_reference, pubmed_id, bud_session):
    urls = []

    from src.sgd.model.bud.reference import Ref_URL

    doi = None
    pubmed_central_id = None
    for ref_url in bud_session.query(Ref_URL).options(joinedload('url')).filter_by(reference_id=bud_reference.id).all():
        urls.append({'display_name': ref_url.url.url_type,
                     'link': ref_url.url.url,
                     'source': {'display_name': ref_url.url.source},
                     'url_type': ref_url.url.url_type,
                     'bud_id': ref_url.id})

        if ref_url.url.url_type == 'PMC full text':
            pubmed_central_id = ref_url.url.url.replace('http://www.ncbi.nlm.nih.gov/pmc/articles/', '')[:-1]
        elif ref_url.url.url_type == 'DOI full text':
            doi = ref_url.url.url[18:]

    if pubmed_id is not None:
        urls.append({'display_name': 'PubMed',
                     'link': 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(pubmed_id),
                     'source': {'display_name': 'PubMed'},
                     'url_type': 'PUBMED'})
    if doi is not None:
        urls.append({'display_name': 'Full-Text',
                     'link': 'http://dx.doi.org/' + doi,
                     'source': {'display_name': 'DOI'},
                     'url_type': 'FULLTEXT'})
    if pubmed_central_id is not None:
        urls.append({'display_name': 'PMC',
                     'link': 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(pubmed_central_id),
                     'source': {'display_name': 'PubMedCentral'},
                     'url_type': 'PUBMEDCENTRAL'})
    return urls, pubmed_central_id, doi


def load_aliases(bud_reference, bud_session):
    aliases = []

    from src.sgd.model.bud.reference import DbxrefRef

    for ref_dbxref in bud_session.query(DbxrefRef).options(joinedload(DbxrefRef.dbxref)).filter_by(reference_id=bud_reference.id).all():
        aliases.append({'display_name': ref_dbxref.dbxref.dbxref_id,
                        'source': {'display_name': 'SGD'},
                        'alias_type': ref_dbxref.dbxref.dbxref_type,
                        'bud_id': ref_dbxref.dbxref.id,
                        'date_created': str(ref_dbxref.dbxref.date_created),
                        'created_by': ref_dbxref.dbxref.created_by})

    return aliases


def load_reftypes(bud_reference, bud_session):
    reftypes = []

    from src.sgd.model.bud.reference import RefReftype

    for old_refreftype in bud_session.query(RefReftype).options(joinedload(RefReftype.reftype)).filter_by(reference_id=bud_reference.id).all():
        reftypes.append({'display_name': old_refreftype.reftype.name,
                         'source': {'display_name': old_refreftype.reftype.source}})
    return reftypes


def reference_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Reference, Ref_URL

    bud_session = bud_session_maker()

    for old_reference in bud_session.query(Reference).order_by(Reference.id.desc()).options(joinedload('book'), joinedload('journal')).all():
        new_journal = None
        old_journal = old_reference.journal
        if old_journal is not None:
            abbreviation = old_journal.abbreviation
            if old_journal.issn == '0948-5023':
                abbreviation = 'J Mol Model (Online)'
            new_journal = {'title': old_journal.full_name,
                           'med_abbr': abbreviation,
                           'source': {'display_name': old_reference.source}}

        new_book = None
        old_book = old_reference.book
        if old_book is not None:
            new_book = {'title': old_book.title,
                        'volume_title': old_book.volume_title,
                        'source': {'display_name': old_reference.source}}

        pubmed_id = None
        if old_reference.pubmed_id is not None:
            pubmed_id = old_reference.pubmed_id

        year = None
        if old_reference.year is not None:
            year = int(old_reference.year)

        urls, pubmed_central_id, doi = load_urls(old_reference, pubmed_id, bud_session)

        obj_json = remove_nones({'bud_id': old_reference.id,
                    'sgdid': old_reference.dbxref_id,
                    'source': {'display_name': old_reference.source},
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

        #Load Reference Reftypes
        obj_json['reference_reftypes'] = load_reftypes(old_reference, bud_session)

        print obj_json['sgdid']

        yield obj_json

    bud_session.close()

# -------------------- Convert Bibentry ---------------------
def make_bibentry_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.reference import Reference, Book, Journal, Author, Reftype
    from src.sgd.model.nex.paragraph import Referenceparagraph
    def bibentry_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_journal = dict([(x.id, x) for x in nex_session.query(Journal).all()])
        id_to_book = dict([(x.id, x) for x in nex_session.query(Book).all()])
        id_to_author = dict([(x.id, x) for x in nex_session.query(Author).all()])
        id_to_reftype = dict([(x.id, x) for x in nex_session.query(Reftype).all()])

        for reference in nex_session.query(Reference).options(joinedload('author_references'), joinedload('ref_reftypes')).all():
            entries = []

            add_entry(entries, reference, lambda x: x.pubmed_id, 'PMID')
            add_entry(entries, reference, lambda x: x.ref_status, 'STAT')
            add_entry(entries, reference, lambda x: x.date_published, 'DP')
            add_entry(entries, reference, lambda x: x.title, 'TI')
            add_entry(entries, reference, lambda x: x.source.display_name, 'SO')
            add_entry(entries, reference, lambda x: x.date_revised, 'LR')
            add_entry(entries, reference, lambda x: x.issue, 'IP')
            add_entry(entries, reference, lambda x: x.page, 'PG')
            add_entry(entries, reference, lambda x: x.volume, 'VI')
            add_entry(entries, reference, lambda x: 'SGD', 'SO')

            for author_reference in reference.author_references:
                author = id_to_author[author_reference.author_id]
                add_entry(entries, author, lambda x: x.display_name, 'AU')

            for ref_reftype in reference.ref_reftypes:
                reftype = id_to_reftype[ref_reftype.reftype_id]
                add_entry(entries, reftype, lambda x: x.display_name, 'PT')

            if len(reference.paragraphs) > 0:
                add_entry(entries, reference, lambda x: reference.paragraphs[0].to_json(), 'AB')

            if reference.journal_id is not None:
                journal = id_to_journal[reference.journal_id]
                add_entry(entries, journal, lambda x: x.med_abbr, 'TA')
                add_entry(entries, journal, lambda x: x.title, 'JT')
                add_entry(entries, journal, lambda x: x.issn_print, 'IS')

            if reference.book is not None:
                book = id_to_book[reference.book_id]
                add_entry(entries, book, lambda x: x.publisher_location, 'PL')
                add_entry(entries, book, lambda x: x.title, 'BTI')
                add_entry(entries, book, lambda x: x.volume_title, 'VTI')
                add_entry(entries, book, lambda x: x.isbn, 'ISBN')

            yield {'id': reference.id,
                   'text': '\n'.join([str(x) for x in entries])}

        bud_session.close()
        nex_session.close()
    return bibentry_starter

def add_entry(entries, reference, value_f, label):
    try:
        value = value_f(reference)
        if value is not None:
            entries.append(label + ' - ' + str(value))
    except:
        pass

# --------------------- Convert Author Reference ---------------------
def make_author_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Author, Reference
    from src.sgd.model.bud.reference import AuthorReference as OldAuthorReference
    def author_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_author = dict([(x.unique_key(), x) for x in nex_session.query(Author).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])

        for old_author_reference in bud_session.query(OldAuthorReference).all():
            author_key = create_format_name(old_author_reference.author.name)
            reference_id = old_author_reference.reference_id
            if author_key in key_to_author and reference_id in id_to_reference:
                yield {'id': old_author_reference.id,
                       'source': key_to_source['PubMed'],
                       'author': key_to_author[author_key],
                       'reference': id_to_reference[reference_id],
                       'order': old_author_reference.order,
                       'author_type': old_author_reference.type,
                       'date_created': old_author_reference.author.date_created,
                       'created_by': old_author_reference.author.created_by}
            else:
                print 'Author or reference not found: ' + str(author_key) + ' ' + str(reference_id)

        bud_session.close()
        nex_session.close()
    return author_reference_starter


# --------------------- Convert Reference Relation ---------------------
def make_reference_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import RefRelation
    def reference_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])
        reference_ids = set(x.id for x in nex_session.query(Reference.id).all())

        for old_ref_relation in bud_session.query(RefRelation).all():
            parent_id = old_ref_relation.parent_id
            child_id = old_ref_relation.child_id
            if parent_id in reference_ids and child_id in reference_ids:
                yield {'source': key_to_source['SGD'],
                       'parent_id': parent_id,
                       'child_id': child_id,
                       'date_created': old_ref_relation.date_created,
                       'created_by': old_ref_relation.created_by}
            else:
                print 'Reference not found: ' + str(parent_id) + ' ' + str(child_id)

        bud_session.close()
        nex_session.close()
    return reference_relation_starter


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, reference_starter, 'reference', lambda x: x['sgdid'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')