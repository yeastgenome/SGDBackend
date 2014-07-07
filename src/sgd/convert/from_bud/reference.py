import datetime

from mpmath import ceil
from sqlalchemy.orm import joinedload
import requests

from src.sgd.model.nex import create_format_name


__author__ = 'kpaskov'

# --------------------- Convert Journal ---------------------
def make_journal_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.reference import Journal
    def journal_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_journal in bud_session.query(Journal).all():
            abbreviation = old_journal.abbreviation
            if old_journal.issn == '0948-5023':
                abbreviation = 'J Mol Model (Online)'

            title = old_journal.full_name
            if title is not None or abbreviation is not None:
                yield {'source': key_to_source['PubMed'],
                       'title': title,
                       'med_abbr': abbreviation,
                       'issn_print': old_journal.issn,
                       'issn_online': old_journal.essn,
                       'date_created': old_journal.date_created,
                       'created_by': old_journal.created_by}

        bud_session.close()
        nex_session.close()
    return journal_starter

# --------------------- Convert Book ---------------------
def make_book_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.reference import Book
    def book_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_book in bud_session.query(Book).all():
            yield {'source': key_to_source['PubMed'],
                   'title': old_book.title,
                   'volume_title': old_book.volume_title,
                   'isbn': old_book.isbn,
                   'total_pages': old_book.total_pages,
                   'publisher': old_book.publisher,
                   'publisher_location': old_book.publisher_location,
                   'date_created': old_book.date_created,
                   'created_by': old_book.created_by}

        bud_session.close()
        nex_session.close()
    return book_starter

# --------------------- Convert Reference ---------------------
def make_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Journal, Book
    from src.sgd.model.bud.reference import Reference, Ref_URL
    def reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_journal = dict([(x.unique_key(), x) for x in nex_session.query(Journal).all()])
        key_to_book = dict([(x.unique_key(), x) for x in nex_session.query(Book).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        reference_id_to_doi = dict([(x.reference_id, x.url.url[18:]) for x in bud_session.query(Ref_URL).options(joinedload('url')).all() if x.url.url_type == 'DOI full text'])
        reference_id_to_pmcid = dict([(x.reference_id, x.url.url.replace('http://www.ncbi.nlm.nih.gov/pmc/articles/', '')[:-1]) for x in bud_session.query(Ref_URL).options(joinedload('url')).all() if x.url.url_type == 'PMC full text'])

        for old_reference in bud_session.query(Reference).order_by(Reference.id.desc()).options(joinedload('book'), joinedload('journal')).all():
            citation = create_citation(old_reference.citation)
            display_name = create_display_name(citation)

            new_journal = None
            old_journal = old_reference.journal
            if old_journal is not None:
                abbreviation = old_journal.abbreviation
                if old_journal.issn == '0948-5023':
                    abbreviation = 'J Mol Model (Online)'
                journal_key = (old_journal.full_name, abbreviation)
                new_journal = None if journal_key not in key_to_journal else key_to_journal[journal_key]

            new_book = None
            old_book = old_reference.book
            if old_book is not None:
                book_key = (old_book.title, old_book.volume_title)
                new_book = None if book_key not in key_to_book else key_to_book[book_key]

            pubmed_id = None
            if old_reference.pubmed_id is not None:
                pubmed_id = old_reference.pubmed_id

            year = None
            if old_reference.year is not None:
                year = int(old_reference.year)

            date_revised = None
            if old_reference.date_revised is not None:
                old_date = str(old_reference.date_revised)
                date_revised = datetime.date(int(old_date[0:4]), int(old_date[4:6]), int(old_date[6:8]))

            source_key = create_format_name(old_reference.source)
            source = None
            if source_key in key_to_source:
                source = key_to_source[source_key]
            else:
                print 'Source not found: ' + source_key
                yield None

            doi = None if old_reference.id not in reference_id_to_doi else reference_id_to_doi[old_reference.id]
            pmcid = None if old_reference.id not in reference_id_to_pmcid else reference_id_to_pmcid[old_reference.id]

            yield {'id': old_reference.id,
                   'display_name': display_name,
                   'sgdid': old_reference.dbxref_id,
                   'source': source,
                   'ref_status': old_reference.status,
                   'pubmed_id': pubmed_id,
                   'fulltext_status': old_reference.pdf_status,
                   'citation': citation,
                   'year': year,
                   'date_published': old_reference.date_published,
                   'date_revised': date_revised,
                   'issue': old_reference.issue,
                   'page': old_reference.page,
                   'volume': old_reference.volume,
                   'title': old_reference.title,
                   'journal': new_journal,
                   'book': new_book,
                   'doi': doi,
                   'pubmed_central_id': pmcid,
                   'date_created': old_reference.date_created,
                   'created_by': old_reference.created_by}

        bud_session.close()
        nex_session.close()
    return reference_starter

def create_citation(citation):
    #end_of_name = citation.find(")")+1
    #name = citation[:end_of_name]
    #words_in_name = name.split()
    #for i in range(0, len(words_in_name)):
    #    word = words_in_name[i]
    #    if len(word) > 3:
    #        words_in_name[i] = word.title()
    #name = ' '.join(words_in_name)
    #new_citation = name + citation[end_of_name:]
    new_citation = citation.replace('()', '')
    return new_citation

def create_display_name(citation):
    display_name = citation[:citation.find(")")+1]
    return display_name

def get_pubmed_central_ids(pubmed_ids, chunk_size=200):
    pubmed_id_to_central_id = {}
    count = len(pubmed_ids)
    num_chunks = ceil(1.0*count/chunk_size)
    min_id = 0
    for _ in range(0, num_chunks):
        try:
            chunk_of_pubmed_ids = pubmed_ids[min_id:min_id+chunk_size]
            url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pmc&id='
            url = url + '&id='.join([str(x) for x in chunk_of_pubmed_ids])
            r = requests.get(url)
            xml = str(r.text)
            pieces = xml.split('<LinkSet>')
            j = 0
            for piece in pieces[1:]:
                pubmed_id = chunk_of_pubmed_ids[j]
                linksets = piece.split('<LinkSetDb>')
                pubmed_id_to_central_id[pubmed_id] = None
                for linkset in linksets[1:]:
                    if '<LinkName>pubmed_pmc</LinkName>' in linkset:
                        pubmed_central_id = int(linkset[linkset.index('<Id>')+4:linkset.index('</Id>')])
                        pubmed_id_to_central_id[pubmed_id] = pubmed_central_id
                j = j+1
        except:
            pass
        min_id = min_id + chunk_size
    return pubmed_id_to_central_id

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

# --------------------- Convert Author ---------------------
def make_author_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.reference import Author
    def author_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])

        for old_author in bud_session.query(Author).all():
            yield {'display_name': old_author.name,
                   'source': key_to_source['PubMed'],
                   'date_created': old_author.date_created,
                   'created_by': old_author.created_by}

        bud_session.close()
        nex_session.close()
    return author_starter

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

# --------------------- Convert Reftype ---------------------
def make_reftype_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.reference import RefType
    def reftype_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])

        for old_reftype in bud_session.query(RefType).all():
            source_key = create_format_name(old_reftype.source)
            source = None if source_key not in key_to_source else key_to_source[source_key]
            yield {'id': old_reftype.id,
                   'display_name': old_reftype.name,
                   'source': source,
                   'date_created': old_reftype.date_created,
                   'created_by': old_reftype.created_by}

        bud_session.close()
        nex_session.close()
    return reftype_starter

# --------------------- Convert ReferenceReftype ---------------------
def make_ref_reftype_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference, Reftype
    from src.sgd.model.bud.reference import RefReftype
    def ref_reftype_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        id_to_reftype = dict([(x.id, x) for x in nex_session.query(Reftype).all()])

        for old_refreftype in bud_session.query(RefReftype).all():
            reference_id = old_refreftype.reference_id
            reftype_id = old_refreftype.reftype_id
            if reference_id in id_to_reference and reftype_id in id_to_reftype:
                reftype = id_to_reftype[reftype_id]
                source = key_to_source[reftype.source.unique_key()]

                yield {'id': old_refreftype.id,
                       'source': source,
                       'reference': id_to_reference[reference_id],
                       'reftype': reftype,
                       'date_created': reftype.date_created,
                       'created_by': reftype.created_by}
            else:
                print 'Reference not found: ' + str(reference_id)

        bud_session.close()
        nex_session.close()
    return ref_reftype_starter

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

# --------------------- Convert Reference Alias ---------------------
def make_reference_alias_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reference as OldReference
    def reference_alias_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])
        reference_ids = set(x.id for x in nex_session.query(Reference.id).all())

        for old_reference in bud_session.query(OldReference).options(joinedload('dbxrefrefs')).all():
            reference_id = old_reference.id
            if reference_id in reference_ids:
                for dbxref in old_reference.dbxrefs:
                    altid_name = dbxref.dbxref_type
                    yield {'display_name': dbxref.dbxref_id,
                            'source': key_to_source['SGD'],
                            'category': altid_name,
                            'reference_id': reference_id,
                            'date_created': old_reference.date_created,
                            'created_by': old_reference.created_by}
            else:
                print 'Reference not found: ' + str(reference_id)
        bud_session.close()
        nex_session.close()
    return reference_alias_starter

# --------------------- Convert Reference URL ---------------------
def make_reference_url_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    def reference_url_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source)])

        for reference in nex_session.query(Reference).all():
            if reference.pubmed_id is not None:
                yield {'display_name': 'PubMed',
                       'link': 'http://www.ncbi.nlm.nih.gov/pubmed/' + str(reference.pubmed_id),
                       'source': key_to_source['PubMed'],
                       'category': 'PUBMED',
                       'reference_id': reference.id}
            if reference.doi is not None:
                yield {'display_name': 'Full-Text',
                       'link': 'http://dx.doi.org/' + reference.doi,
                       'source': key_to_source['DOI'],
                       'category': 'FULLTEXT',
                       'reference_id': reference.id}
            if reference.pubmed_central_id is not None:
                yield {'display_name': 'PMC',
                       'link': 'http://www.ncbi.nlm.nih.gov/pmc/articles/' + str(reference.pubmed_central_id),
                       'source': key_to_source['PubMedCentral'],
                       'category': 'PUBMEDCENTRAL',
                       'reference_id': reference.id}

        bud_session.close()
        nex_session.close()
    return reference_url_starter