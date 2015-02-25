__author__ = 'kpaskov'

import author
import book
import journal
import keyword
import locus
import reftype
import source

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