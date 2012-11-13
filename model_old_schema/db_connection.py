'''
Created on Oct 18, 2012

@author: kpaskov

This class is used to perform queries and operations on the corresponding database. In this case, the BUD schema on fasolt.

'''
from lit_review.parse import TaskType
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
        """
        Create engine, associate metadata with the engine, then create a SessionFactory for use through the backend.
        """
        self.engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, username, password, DBHOST, DBNAME), convert_unicode=True)
        Base.metadata.bind = self.engine
        self.SessionFactory = sessionmaker(bind=self.engine)
        model_old_schema.current_user = username
        return
    
    def isConnected(self):
        """
        Checks if a connection to the db has been made.
        """
        try:
            self.engine.connect()
            return True
        except:                 
            traceback.print_exc(file=sys.stdout)
            return False
    
    def getFeatureByName(self, name):
        """
        Get a feature by its name.
        """
        try:
            from model_old_schema.feature import Feature
            session = self.SessionFactory()
            return session.query(Feature).filter(or_(Feature.name == name.upper()), Feature.gene_name == name.upper()).first();
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
    
    def getRefTempByPmid(self, pubmed_id):
        """
        Get a feature by its pubmed_id.
        """
        try:
            from model_old_schema.reference import RefTemp
            session = self.SessionFactory()
            pubmed_id_as_int = int(float(pubmed_id))
            return session.query(RefTemp).filter_by(pubmed_id=pubmed_id_as_int).first();
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
    
    def getRefTemps(self):
        """
        Get all RefTemps.
        """
        try:
            from model_old_schema.reference import RefTemp
            session = self.SessionFactory()
            return session.query(RefTemp).all()
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
    
    def moveRefTempToRefBad(self, pubmed_id):
        """"
        Remove reference from the RefTemp table and add it to the RefBad table.
        """
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
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            session.close()
            
    def moveRefTempToReference(self, pubmed_id):
        """
        Remove reference from the RefTemp table, create a full Reference, and add it to the Reference table.
        """
        try:       
            session = self.SessionFactory()
            r_temp = self.getRefTempByPmid(pubmed_id)
            r = self.createReference(r_temp)
            
            session.add(r)
            session.delete(r_temp)
            session.commit()
            return True
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            session.close()
            
    def validateGenes(self, gene_names):
        """
        Convert a list of gene_names to a mapping between those gene_names and features.
        """
        try:
            from model_old_schema.feature import Feature
            session = self.SessionFactory()
            upper_gene_names = [x.upper() for x in gene_names]
            fs = session.query(Feature).filter(or_(Feature.name.in_(upper_gene_names), Feature.gene_name.in_(upper_gene_names))).all()
            
            name_to_feature = {}
            for f in fs:
                name_to_feature[f.name] = f
                name_to_feature[f.gene_name] = f
            
            extraneous_names = name_to_feature.keys()
            for name in upper_gene_names:
                extraneous_names.remove(name.upper())
            
            for name in extraneous_names:
                del name_to_feature[name]
             
            return name_to_feature
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
            
    def createReference(self, ref_temp):
        """
        Create a Reference from a RefTemp. First grab information on the Reference from NCBI using FetchMedline().
        Then create the reference with its associated object: Journal, Abstract, Author, RefType.
        """
        try:
            pubmed_id = ref_temp.pubmed_id
            
            session = self.SessionFactory()

            #Check if reference already exists.
            from model_old_schema.reference import Reference, Journal, Author, RefType
            ref = get_or_create(session, Reference, pubmed_id=pubmed_id)
            
            #Get medline record from ncbi
            medline = FetchMedline(pubmed_id)
            records = medline.get_records()
            for rec in records:
                record = rec
            pubmed = Pubmed(record)
            
            #Set basic information for the reference.
            ref.status = pubmed.publish_status
            ref.citation = pubmed.citation
            ref.year = pubmed.year
            ref.pdf_status = pubmed.pdf_status
            ref.pages = pubmed.pages
            ref.volume = pubmed.volume
            ref.title = pubmed.title
            ref.issue = pubmed.issue
                
            #Add the journal.
            ref.journal = get_or_create(session, Journal, abbreviation=pubmed.journal_abbrev)
                
            #Add the abstract.
            abstract_txt = pubmed.abstract_txt
            if abstract_txt != '':
                ref.abstract = abstract_txt
                    
            #Add the authors.
            order = 0
            for author_name in pubmed.authors:
                order += 1
                ref.authors[order] = get_or_create(session, Author, name=author_name)
                    
            #Add the ref_type
            ref.refType = get_or_create(session, RefType, name=pubmed.pub_type)
                                
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
            
    def associate(self, reference, name_to_feature, tasks):
        """
        Associate a Reference with LitGuide entries.
        """
        try:
            from model_old_schema.admin import RefCuration
            from model_old_schema.reference import LitGuide
            session = self.SessionFactory()
                        
            for task in tasks:
                
                #Convert gene_names to features using the name_to_feature table.                
                features = set()
                for gene_name in task.gene_names:
                    features.add(name_to_feature[gene_name])
                
                if len(features) > 0:
                    ## Create RefCuration objects and add them to the Reference.
                    for feature in features:
                        curation = get_or_create(session, RefCuration, reference_id = reference.id, task = task.name, feature_id = feature.id)
                        curation.comment = task.comment
                        reference.curation.append(curation)
                            
                    ## Create a LitGuide object and attach features to it.
                    lit_guide = get_or_create(session, LitGuide, topic=task.topic, reference_id=reference.id)
                    for feature in features:
                        if not feature.id in lit_guide.feature_ids:
                            lit_guide.features.append(feature)
                    
                else:   ## no gene name provided

                    ## if no gene name provided and "Add to database" was checked,
                    ## no need to add any association
                    if task.type == TaskType.ADD_TO_DATABASE:
                        continue

                    ## if it is a review, no need to add to ref_curation
                    if task.type == TaskType.REVIEWS:
                        ## topic = task = 'Reviews'
                        reference.litGuideTopics.append(task.topic)

                    curation = get_or_create(session, RefCuration, reference_id = reference.id, task=task.name, feature_id=None)
                    curation.comment = task.comment
                    
            
                    ## Create a LitGuide object.
                    if task.type == TaskType.HTP_PHENOTYPE_DATA or task.type == TaskType.REVIEWS:
                        lit_guide = get_or_create(session, LitGuide, topic=task.topic, reference_id=reference.id)
                
                session.commit()
                return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            session.rollback()
            return False
        finally:
            session.close()
    
    def getReferenceByID(self, reference_id):
        from model_old_schema.reference import Reference
        session = self.SessionFactory()
        return session.query(Reference).filter_by(id = reference_id).first()
    
    def getReferenceByPmid(self, pmid):
        from model_old_schema.reference import Reference
        session = self.SessionFactory()
        return session.query(Reference).filter_by(pubmed_id = pmid).first()

def get_or_create(session, model, **kwargs):
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
        return instance
    
if __name__ == '__main__':
    conn = DBConnection()
    conn.connect(DBUSER, DBPASS)
    #r = conn.getRefTempByPmid(23118484)
    #print conn.moveRefTempToReference(22888114)
    #print r
    #result = conn.createReference(r)
    #print result
    r = conn.getReferenceByPmid(22888114)
    print r
    print r.journal
    
    