__author__ = 'kpaskov'

from src.sgd.convert.into_curate import author, book, journal, keyword, locus, reftype, source

if __name__ == '__main__':
    bud_db = 'pastry.stanford.edu:1521'
    nex_db = 'curator-dev-db'

    #Misc
    source.convert(bud_db, nex_db)
    keyword.convert(bud_db, nex_db)

    #Locus
    locus.convert(bud_db, nex_db)

    #Reference
    book.convert(bud_db, nex_db)
    journal.convert(bud_db, nex_db)
    reftype.convert(bud_db, nex_db)
    author.convert(bud_db, nex_db)