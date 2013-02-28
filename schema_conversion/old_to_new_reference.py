'''
Created on Feb 27, 2013

@author: kpaskov
'''


new_refs = {}
new_journals = {}
new_books = {}
new_abstracts = {}
new_author_refs = {}
new_authors = {}
new_ref_types = {}

def fix_references_with_same_name(session):
    name_to_refs = {}
    for r in new_refs.values():
        if r.name in name_to_refs:
            name_to_refs[r.name].append(r)
        else:
            name_to_refs[r.name] = [r]
    
    for ref_list in name_to_refs.values():
        if len(ref_list) > 1:
            sorted_list = sorted(ref_list, key=lambda x: x.pubmed_id)
            i = 0
            for ref in sorted_list:
                if i < 26:
                    name = ref.name + chr(i+97)
                else:
                    name = ref.name + 'a' + chr(i+97-26)
                    
                i=i+1
                ref.name = name
    session.commit()
                

def check_value(new_obj, old_obj, field_name):
    new_obj_value = getattr(new_obj, field_name)
    old_obj_value = getattr(old_obj, field_name)
    if new_obj_value != old_obj_value:
        setattr(new_obj, field_name, old_obj_value)
        #print field_name + ' for ' + new_obj.__class__.__name__ + ' ' + str(new_obj.id) + ' changed from ' + str(new_obj_value) + ' to ' + str(old_obj_value)

def clean_citation(citation):
    end_of_name = citation.find(")")+1
    name = citation[:end_of_name]
    words_in_name = name.split()
    for i in range(0, len(words_in_name)):
        word = words_in_name[i]
        if len(word) > 3:
            words_in_name[i] = word.title()
    name = ' '.join(words_in_name)
    return name + citation[end_of_name:]
  
def citation_to_name(citation):
    name = citation[:citation.find(")")+1]
    return name

def reference_to_reference(reference):
    from model_new_schema.reference import Reference as NewReference
    
    #Create ref with basic information
    new_ref = new_refs[reference.id]
    
    old_citation = clean_citation(reference.citation)
    old_name = citation_to_name(old_citation)
    if new_ref is None:
        new_ref = NewReference(reference.pubmed_id, reference_id=reference.id, source=reference.source, status=reference.status, pdf_status=reference.pdf_status, 
                        dbxref_id=reference.dbxref_id, citation=old_citation, year=reference.year, date_published=reference.date_published,
                        date_revised=reference.date_revised, issue=reference.issue, page=reference.page, volume=reference.volume, title=reference.title,
                        journal_id=reference.journal_id, book_id=reference.book_id, doi=reference.doi, name=old_citation, date_created=reference.date_created, created_by=reference.created_by)
    else:
        #Check that basic information is correct.
        check_value(new_ref, reference, 'pubmed_id')
        check_value(new_ref, reference, 'source')
        check_value(new_ref, reference, 'status')
        check_value(new_ref, reference, 'pdf_status')
        check_value(new_ref, reference, 'dbxref_id')
        check_value(new_ref, reference, 'year')
        check_value(new_ref, reference, 'date_published')
        check_value(new_ref, reference, 'date_revised')
        check_value(new_ref, reference, 'issue')
        check_value(new_ref, reference, 'page')
        check_value(new_ref, reference, 'volume')
        check_value(new_ref, reference, 'title')
        check_value(new_ref, reference, 'journal_id')
        check_value(new_ref, reference, 'book_id')
        check_value(new_ref, reference, 'doi')
        check_value(new_ref, reference, 'date_created')
        check_value(new_ref, reference, 'created_by')
        
        if new_ref.citation != old_citation:
            new_ref.citation = old_citation
            
        if new_ref.name != old_name:
            new_ref.name = old_name
    
    #Create journal and add it to reference.
    if reference.journal is not None:
        new_j = journal_to_journal(reference.journal)
        new_ref.journal = new_j
                  
    #Create book and add it to reference  
    if reference.book is not None:
        new_b = book_to_book(reference.book)
        new_ref.book = new_b
                    
    #Create abstract and add it to reference
    #if reference.abst is not None:
    #    new_a = abstract_to_abstract(reference.abst)
    #new_ref.abst = new_a
              
    #Create author_references and authors and add them to reference      
    #author_ids = set()
    #for index, author_reference in reference.author_references.items():
    #    author_reference = author_reference_to_author_reference(author_reference)
    #    if not author_reference.author_id in author_ids:
    #        new_ref.author_references[index] = author_reference
    #        author_ids.add(author_reference.author_id)
    #    else:
    #        print "Double author in " + str(reference.id) + " author_id =" + str(author_reference.author_id)
                
    #Create reftypes and add them to reference
    for mapping_id, reftype in reference.reftypes.items():
        new_rt = reftype_to_reftype(reftype)
        new_ref.reftypes[mapping_id] = new_rt
                    
    return new_ref

def book_to_book(book):
    from model_new_schema.reference import Book as NewBook
    
    new_book = new_books[book.id]
    if new_book is None:
        new_book = NewBook(book.title, book.volume_title, book.isbn, book.total_pages, book.publisher, book.publisher_location, 
                    book_id=book.id, date_created=book.date_created, created_by=book.created_by)
    else:
        check_value(new_book, book, 'title')
        check_value(new_book, book, 'volume_title')
        check_value(new_book, book, 'isbn')
        check_value(new_book, book, 'total_pages')
        check_value(new_book, book, 'publisher')
        check_value(new_book, book, 'publisher_location')
        check_value(new_book, book, 'date_created')
        check_value(new_book, book, 'created_by')
        
    return new_book

def journal_to_journal(journal):
    from model_new_schema.reference import Journal as NewJournal
    
    new_journal = new_journals[journal.id]
    if new_journal is None:
        new_journal = NewJournal(journal.abbreviation, journal_id=journal.id, full_name=journal.full_name, issn=journal.issn, essn=journal.essn,
                          created_by=journal.created_by, date_created = journal.date_created)
    else:
        check_value(new_journal, journal, 'full_name')
        check_value(new_journal, journal, 'abbreviation')
        check_value(new_journal, journal, 'issn')
        check_value(new_journal, journal, 'essn')
        check_value(new_journal, journal, 'publisher')
        check_value(new_journal, journal, 'created_by')
        check_value(new_journal, journal, 'date_created')
        
    return new_journal

def author_reference_to_author_reference(author_reference):
    from model_new_schema.reference import AuthorReference as NewAuthorReference
    
    new_author_reference = new_author_refs[author_reference.id]
    new_author = author_to_author(author_reference.author)

    if new_author_reference is None:
        new_author_reference = NewAuthorReference(new_author, author_reference.order, author_reference.type, author_reference_id=author_reference.id)
    else:
        check_value(new_author_reference, author_reference, 'author_id')
        check_value(new_author_reference, author_reference, 'reference_id')
        check_value(new_author_reference, author_reference, 'order')
        check_value(new_author_reference, author_reference, 'type')
    
    new_author_reference.author = new_author
    
    return new_author_reference

def author_to_author(author):
    from model_new_schema.reference import Author as NewAuthor
    
    new_author = new_authors[author.id]
    if new_author is None:
        new_author = NewAuthor(author.name, author_id=author.id, created_by=author.created_by, date_created=author.date_created)
    else:
        check_value(new_author, author, 'name')
        check_value(new_author, author, 'created_by')
        check_value(new_author, author, 'date_created')
        
    return new_author

def abstract_to_abstract(abstract):
    from model_new_schema.reference import Abstract as NewAbstract
    
    new_abstract = new_abstracts[abstract.reference_id]
    if new_abstract is None:
        new_abstract = NewAbstract(abstract.text, abstract.reference_id)
    else:
        check_value(new_abstract, abstract, 'text')
        
    return new_abstract

def reftype_to_reftype(reftype):
    from model_new_schema.reference import Reftype as NewReftype
    
    new_reftype = new_ref_types[reftype.id]
    if new_reftype is None:
        new_reftype = NewReftype(reftype.name, reftype_id=reftype.id, source=reftype.source, created_by=reftype.created_by, date_created=reftype.date_created)
    else:
        check_value(new_reftype, reftype, 'source')
        check_value(new_reftype, reftype, 'name')
        check_value(new_reftype, reftype, 'created_by')
        check_value(new_reftype, reftype, 'date_created')
        
    return new_reftype
