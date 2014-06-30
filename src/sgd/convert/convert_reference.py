from src.sgd.model import bud, nex
from src.sgd.convert import prepare_schema_connection, config, clean_up_orphans
from src.sgd.convert.transformers import do_conversion, Obj2NexDB, Json2Obj
__author__ = 'kpaskov'

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    # ------------------------------------------ Reference ------------------------------------------
    # Bud -> Nex
    from src.sgd.model.nex.reference import Reference, Journal, Book, Author, Referencealias, Referenceurl, \
        Referencerelation, Bibentry, AuthorReference, ReferenceReftype, Reftype
    from src.sgd.model.nex.misc import Alias, Relation, Url
    from src.sgd.model.nex.auxiliary import Disambig
    from src.sgd.convert.from_bud.reference import make_reference_starter, make_journal_starter, make_book_starter,\
        make_bibentry_starter, make_reftype_starter, make_reference_alias_starter, \
        make_author_reference_starter, make_author_starter, make_ref_reftype_starter, make_reference_relation_starter, \
        make_reference_url_starter
    from src.sgd.convert.from_bud.auxiliary import make_disambig_starter

    do_conversion(make_journal_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Journal),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Journal),
                             name='convert.from_bud.journal',
                             delete_untouched=True,
                             commit=True)])

    do_conversion(make_book_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Book),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Book),
                             name='convert.from_bud.book',
                             delete_untouched=True,
                             commit=True)])

    do_conversion(make_reference_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Reference),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Reference),
                             name='convert.from_bud.reference',
                             delete_untouched=True,
                             commit_interval=1000)])

    do_conversion(make_author_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Author),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Author),
                             name='convert.from_bud.author',
                             delete_untouched=True,
                             commit_interval=1000)])

    do_conversion(make_disambig_starter(nex_session_maker, Reference, ['id', 'sgdid', 'pubmed_id', 'doi'], 'REFERENCE', None),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'REFERENCE'),
                             name='convert.from_bud.reference.disambig',
                             delete_untouched=True,
                             commit=True)])

    do_conversion(make_disambig_starter(nex_session_maker, Author, ['format_name', 'id'], 'AUTHOR', None),
                  [Json2Obj(Disambig),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Disambig).filter(Disambig.class_type == 'AUTHOR'),
                             name='convert.from_bud.author.disambig',
                             delete_untouched=True,
                             commit=True)])

    do_conversion(make_author_reference_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(AuthorReference),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(AuthorReference),
                             name='convert.from_bud.author_reference',
                             delete_untouched=True,
                             commit_interval=1000)])

    do_conversion(make_reftype_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Reftype),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Reftype),
                             name='convert.from_bud.reftype',
                             delete_untouched=True,
                             commit=True)])

    do_conversion(make_ref_reftype_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(ReferenceReftype),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(ReferenceReftype),
                             name='convert.from_bud.reference_reftype',
                             delete_untouched=True,
                             commit_interval=1000)])

    do_conversion(make_bibentry_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Bibentry),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Bibentry),
                             name='convert.from_bud.bibentry',
                             delete_untouched=True,
                             commit_interval=1000)])

    do_conversion(make_reference_relation_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referencerelation),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referencerelation),
                             name='convert.from_bud.reference_relation',
                             delete_untouched=True,
                             commit_interval=1000,
                             already_deleted=clean_up_orphans(nex_session_maker, Referencerelation, Relation, 'REFERENCE'))])

    do_conversion(make_reference_alias_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referencealias),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referencealias),
                             name='convert.from_bud.reference_alias',
                             delete_untouched=True,
                             commit_interval=1000,
                             already_deleted=clean_up_orphans(nex_session_maker, Referencealias, Alias, 'REFERENCE'))])

    do_conversion(make_reference_url_starter(bud_session_maker, nex_session_maker),
                  [Json2Obj(Referenceurl),
                   Obj2NexDB(nex_session_maker, lambda x: x.query(Referenceurl),
                             name='convert.from_bud.reference_url',
                             commit_interval=1000,
                             delete_untouched=True,
                             already_deleted=clean_up_orphans(nex_session_maker, Referenceurl, Url, 'REFERENCE'))])
