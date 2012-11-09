'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the BUD schema on fasolt.

'''
from lit_review.pubmed import FetchMedline, Pubmed
from model_old_schema import Base
from model_old_schema.config import DBTYPE, DBHOST, DBNAME, DBUSER, DBPASS
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import or_
import model_old_schema
import sys
import traceback

# imports of model classes from model.feature, model.taxonomy, etc are done as needed, since these imports are
# not available until AFTER the metadata is bound to the engine.

class DBConnection(object):
    '''
    This class acts as a divider between the Oracle back-end and the application. In order to pull information
    from the Oracle DB, this class MUST be called.
    '''
    engine = None
    SessionFactory = None

         
    def connect(self, username, password):
        #Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True)
        Base.metadata.bind = self.engine
        self.SessionFactory = sessionmaker(bind=self.engine)
        model_old_schema.current_user = username
        return
    
    def isConnected(self):
        #Checks if a connection to the db has been made.
        try:
            self.engine.connect()
            return True
        except:
            return False
    
    def getFeatureByName(self, name):
        #Get a feature by its name.
        try:
            from model_old_schema.feature import Feature
            session = self.SessionFactory()
            return session.query(Feature).filter_by(name=name).first();
        finally:
            session.close()
    
    def getRefTempByPmid(self, pubmed_id):
        #Get a feature by its pubmed_id.
        try:
            from model_old_schema.reference import RefTemp
            session = self.SessionFactory()
            pubmed_id_as_int = int(float(pubmed_id))
            return session.query(RefTemp).filter_by(pubmed_id=pubmed_id_as_int).first();
        finally:
            session.close()
    
    def getRefTemps(self):
        #Get all RefTemps.
        try:
            from model_old_schema.reference import RefTemp
            session = self.SessionFactory()
            return session.query(RefTemp).all()
        finally:
            session.close()
    
    def moveRefTempToRefBad(self, pubmed_id):
        #Remove reference from the RefTemp table and add it to the RefBad table.
        try:       
            from model_old_schema.reference import RefBad
            session = self.SessionFactory()
            r_temp = self.getRefTempByPmid(pubmed_id)
            r_bad = RefBad(r_temp.pubmed_id)
            session.add(r_bad)
            session.delete(r_temp)
            session.commit()
            return True
        except:
            session.rollback()
            return False
        finally:
            session.close()
            
    def validateGenes(self, gene_names):
        #Convert a list of gene_names to a list of features.
        try:
            from model_old_schema.feature import Feature
            session = self.SessionFactory()
            upper_gene_names = [x.upper() for x in gene_names]
            return session.query(Feature).filter(or_(Feature.name.in_(upper_gene_names), Feature.gene_name.in_(upper_gene_names))).all()
        finally:
            session.close()
            
    def createReference(self, ref_temp):
        try:
            pubmed_id = ref_temp.pubmed_id
            
            session = self.SessionFactory()

            #Check if reference already exists.
            from model_old_schema.reference import Reference, Journal, Author, RefType
            ref = session.query(Reference).filter_by(pubmed_id=pubmed_id).first()
            if ref:
                return ref
            else:
                #Get medline record from ncbi
                medline = FetchMedline(pubmed_id)
                records = medline.get_records()
                for rec in records:
                    record = rec
                pubmed = Pubmed(record)
                
                #Create the reference.
                ref = Reference(pubmed.publish_status,
                             pubmed.citation,
                             pubmed.year,
                             pubmed_id,
                             'PubMed script',
                             pubmed.pdf_status,
                             pubmed.pages,
                             pubmed.volume,
                             pubmed.title,
                             pubmed.issue)
                
                #Add the journal.
                journal_abbrev = pubmed.journal_abbrev
                journal = session.query(Journal).filter_by(abbreviation=journal_abbrev).first()
                if not journal:
                    journal = Journal(journal_abbrev)
                ref.journal = journal
                
                #Add the abstract.
                abstract_txt = pubmed.abstract_txt
                if abstract_txt != '':
                    ref.abstract = abstract_txt
                    
                #Add the authors.
                order = 0
                for author_name in pubmed.authors:
                    order += 1
                    author = session.query(Author).filter_by(name=author_name).first()
                    if author:
                        ref.authors[order] = author
                    else:
                        ref.authorNames[order] = author_name
                    
                #Add the ref_type
                refTypeName = pubmed.pub_type
                refType = session.query(RefType).filter_by(name=refTypeName).first()
                if refType:
                    ref.refTypes.append(refType)
                else:
                    ref.refTypeNames.append(refTypeName)
                                
                #Add the new ref to the session.
                session.add(ref)
                session.commit()        
                return ref
        except Exception:
            traceback.print_exc(file=sys.stdout)
            session.rollback()
            return False
        finally:
            session.close()
            
    def getReferenceByPmid(self, pubmed_id):
        #Get all RefTemps.
        try:
            from model_old_schema.reference import Reference
            session = self.SessionFactory()
            r = session.query(Reference).first();
            return r
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()

        
if __name__ == '__main__':
    conn = DBConnection()
    conn.connect(DBUSER, DBPASS)
    #r = conn.getRefTempByPmid(23118484)
    conn.getFirstReference(23118484)
    #print r
    #result = conn.createReference(r)
    #print result
    #conn.getFirstReference()
    
    