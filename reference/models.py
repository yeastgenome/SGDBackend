"""
Name: models.py

This module contains code/routines used to create flask application,
load the database configuration, create SQLAlchemy object (by passing
the 'app' to it). The SQLAlchemy object (db) provides the declarative
base 'Model' for declaring models (eg, feature, seq, etc classes).

Shuai Weng, 7/2012

"""

from flask import Flask, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import (create_engine, func)
from config import DBTYPE
from config import DBUSER
from config import DBPASS
from config import DBHOST
from config import DBNAME
from config import SCHEMA
from medline_journal import MedlineJournal
from pubmed import FetchMedline
from pubmed import Pubmed

app = Flask(__name__)

## http://packages.python.org/Flask-SQLAlchemy/config.html
## how to adjust these parameters to make sure it won't timeout??
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME)
app.config['SQLALCHEMY_POOL_SIZE'] = 10 ## default = 5 
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 50 ## default = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800 # 30min

db = SQLAlchemy(app)
meta =  db.MetaData(bind=db.engine)

class Database():

    def __init__(self, user, password):
#        db.seesion.dispose()
#        db.session.recreate()
        app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % (DBTYPE, user, password, DBHOST, DBNAME)
        db = SQLAlchemy(app)
        # db.init_app(app)
        meta = db.MetaData(bind=db.engine)
        
    @classmethod
    def connect(self, user, password):
        engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, user, password, DBHOST, DBNAME))
        try:
            engine.connect()
        except:
            return -1
        return 0


## reference/lit_guide related tables
    
class RefTemp(db.Model):
    ## how do we set this in a generic way
    __table__ = db.Table('ref_temp', meta, autoload=True, schema="%s" % (SCHEMA))

    @classmethod
    def delete(self, pmid):
        ref_query = self.query.filter_by(pubmed=pmid)
        row = ref_query.first()
        if row:
            db.session.delete(row)

    @classmethod
    def search(self, pmid=None):
        if pmid == None:
            ref_query = self.query.filter_by()
        else:
            ref_query = self.query.filter_by(pubmed=pmid)
        return ref_query


class RefBad(db.Model):
    __table__ = db.Table('ref_bad', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, pubmed, user, dbxref_id=None):
        self.pubmed = pubmed
        self.dbxref_id = dbxref_id
        self.created_by = user
        
    @classmethod
    def insert(self, pmid, user):
        refbad_query = self.query.filter_by(pubmed=pmid)
        if refbad_query.first():
            return
        ref_bad = self(pmid, user)
        db.session.add(ref_bad)

        
class Abstract(db.Model):
    __table__ = db.Table('abstract', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, ref_no, abstract_txt):
        self.reference_no = ref_no
        self.abstract = abstract_txt

    @classmethod
    def insert(self, ref_no, abs_txt):
        if abs_txt != '':
            abs_entry = self(ref_no, abs_txt)
            db.session.add(abs_entry)


class Author(db.Model):
    __table__ = db.Table('author', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, author_name, user):
        self.author_name = author_name
        self.created_by = user
        
    @classmethod
    def insert(self, name, user):
        author_query = self.query.filter_by(author_name=name)
        if author_query.first():
            return author_query.first().author_no
        author_entry = self(name, user)
        db.session.add(author_entry)
        db.session.commit()
        return author_entry.author_no
    

class AuthorEditor(db.Model):
    __table__ = db.Table('author_editor', meta, autoload=True, schema="%s" % (SCHEMA))
    
    def __init__(self, author_no, ref_no, author_order, author_type='Author'):
        self.author_no = author_no
        self.reference_no = ref_no
        self.author_order = author_order
        self.author_type = author_type

    @classmethod
    def insert(self, author_no, ref_no, author_order):
        author_editor_entry = self(author_no, ref_no, author_order)
        db.session.add(author_editor_entry)
        db.session.commit()


class Journal(db.Model):
    __table__ = db.Table('journal', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, user, abbrev, full_nm=None, issn=None, essn=None, publisher=None):
        self.abbreviation = abbrev
        self.full_name = full_nm
        self.issn = issn
        self.essn = essn
        self.publisher = publisher
        self.created_by = user
        
    @classmethod
    def insert(self, abbrev, user):
        ## should we move this checking part to somewhere else
        journal_query =self.query.filter_by(abbreviation=abbrev)
        if journal_query.first():
            return journal_query.first().journal_no
        medlineJournal = MedlineJournal(abbrev)
        journal_entry = self(user,
                             abbrev,
                             medlineJournal.journal_title,
                             medlineJournal.issn,
                             medlineJournal.essn)
        db.session.add(journal_entry)
        db.session.commit()
        return journal_entry.journal_no


class RefType(db.Model):
    __table__ = db.Table('ref_type', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, reftype, user, source='NCBI'):
        self.ref_type = reftype
        self.source = source
        self.created_by = user

    @classmethod
    def insert(self, pubtype, ref_no, source, user):
        reftype_query = self.query.filter_by(ref_type=pubtype,
                                             source=source)
        reftype_no = 0
        if reftype_query.first():
            reftype_no = reftype_query.first().ref_type_no
        else:
            reftype_entry = self(pubtype, user, source)
            db.session.add(reftype_entry)
            db.session.commit()
            reftype_no = reftype_entry.ref_type_no
        refreftype_entry = RefRefType(ref_no, reftype_no)
        db.session.add(refreftype_entry)
        db.session.commit()
    

class RefRefType(db.Model):
    __table__ = db.Table('ref_reftype', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, ref_no, reftype_no):
        self.reference_no = ref_no
        self.ref_type_no = reftype_no
        
        
class Reference(db.Model):
    __table__ = db.Table('reference', meta, autoload=True, schema="%s" % (SCHEMA))

    ## how to simplify this - so ugly...
    def __init__(self, user, status, citation, year, pubmed, source='PubMed script', pdf_status='N', page=None, volume=None, title=None, issue=None, journal_no=None, doi=None, book_no=None):
        self.status = status
        self.citation = citation
        self.year = year
        self.pubmed = pubmed
        self.source = source
        self.pdf_status = pdf_status
        self.page = page
        self.volume = volume
        self.title = title
        self.issue = issue
        self.journal_no = journal_no
        self.doi = doi
        self.book_no = book_no
        self.created_by = user

    def __repr__(self):
        return '<reference %r>' % self.citation

    @classmethod
    def insert(self, pmid, user):
        
        medline = FetchMedline([pmid])
        records = medline.get_records()

        ## it is weird you can't do record = records[0]??
        for rec in records:
            record = rec

        # get pubmed instance
        pubmed = Pubmed(record)
        
        # insert journal
        journal_no = Journal.insert(pubmed.journal_abbrev, user)

        # insert reference
        ref_no = 0
        ref_query = self.query.filter_by(pubmed=pmid)
        if ref_query.first():
            ref_no = ref_query.first().reference_no
        else:
            ref_entry = self(user,
                             pubmed.publish_status,
                             pubmed.citation,
                             pubmed.year,
                             pmid,
                             'PubMed script',
                             pubmed.pdf_status,
                             pubmed.pages,
                             pubmed.volume,
                             pubmed.title,
                             pubmed.issue,
                             journal_no)
            db.session.add(ref_entry)
            db.session.commit()        
            ref_no = ref_entry.reference_no

        # insert abstract
        Abstract.insert(ref_no, pubmed.abstract_txt)

        # insert author
        order = 0
        for name in pubmed.authors:
            order += 1
            author_no = Author.insert(name, user)
            AuthorEditor.insert(author_no, ref_no, order) 

        # insert ref_type
        RefType.insert(pubmed.pub_type, ref_no, 'NCBI', user)

        return ref_no


class LitGuide(db.Model):
    __table__ = db.Table('lit_guide', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, reference_no, topic, user):
        self.reference_no = reference_no
        self.literature_topic = topic
        self.created_by = user

    @classmethod
    def insert(self, ref_no, topic, user):
        litguide_query = self.query.filter_by(reference_no=ref_no,
                                              literature_topic=topic)
        if litguide_query.first():
            return litguide_query.first().lit_giude_no
        litguide_entry = self(ref_no, topic, user)
        db.session.add(litguide_entry)
        db.session.commit()
        return litguide_entry.lit_guide_no
        
                                          
class RefCuration(db.Model):
    __table__ = db.Table('ref_curation', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, reference_no, task, user, feature_no=None, comment=None):
        self.reference_no = reference_no
        self.curation_task = task
        self.feature_no = feature_no
        self.curator_comment = comment
        self.created_by = user

    @classmethod
    def insert(self, ref_no, task, user, feat_no=None, comment=None):
        refcuration_query = self.query.filter_by(reference_no=ref_no,
                                                 curation_task=task,
                                                 feature_no=feat_no)
        if refcuration_query.first():
            return
        refcuration_entry = self(ref_no, task, user, feat_no, comment)
        db.session.add(refcuration_entry)
        
                                          
class LitGuideFeat(db.Model):
    __table__ = db.Table('litguide_feat', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, feature_no, lit_guide_no):
        self.feature_no = feature_no
        self.lit_guide_no = lit_guide_no
        
    @classmethod
    def insert(self, feat_no, litguide_no):
        lf_query = self.query.filter_by(feature_no=feat_no,
                                        lit_guide_no=litguide_no)
        if lf_query.first():
            return
        lf_entry = self(feat_no, litguide_no)
        db.session.add(lf_entry)


### feature/seq tables

class Feature(db.Model):
    __table__ = db.Table('feature', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, taxon_id, feature_name, feature_type, source='SGD', status='Active', gene_name=None):
        self.taxon_id = taxon_id
        self.feature_name = feature_name
        self.feature_type = feature_type
        self.source = source
        self.status = status
        self.gene_name = gene_name

    def __repr__(self):
        return '<feature %r>' % self.feature_name

    @classmethod
    def search(self, name):
        feat_entry = Feature.query.filter(
            (func.upper(Feature.feature_name) == name.upper()) |
            (func.upper(Feature.gene_name) == name.upper()))
        return feat_entry.first()
        

###
       
class Seq(db.Model):
    __table__ = db.Table('seq', meta, autoload=True, schema="%s" % (SCHEMA))

    def __init__(self, feature_no, seq_type, seq_version, is_current, seq_length, residues, source='SGD'):
        self.feature_no = feature_no
        self.seq_type = seq_type
        self.seq_version = seq_version
        self.is_current = is_current
        self.seq_length = seq_length
        self.residues = residues
        self.source = source
              
    def __repr__(self):
        return '<seq %r>' % self.seq_no
       
###        

class Dbuser(db.Model):
    __table__ = db.Table('dbuser', meta, autoload=True, schema="%s" % (SCHEMA))

    @classmethod
    def search(self, name):
        dbuser_entry = Dbuser.query.filter(func.upper(Dbuser.userid) == name.upper());
        if dbuser_entry.first() and dbuser_entry.first().status == 'Current':
            return dbuser_entry.first()
        return None            
