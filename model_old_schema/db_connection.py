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
    
    def is_connected(self):
        """
        Checks if a connection to the db has been made.
        """
        try:
            self.engine.connect()
            return True
        except:                 
            traceback.print_exc(file=sys.stdout)
            return False
    
    def get_feature_by_name(self, name):
        """
        Get a feature by its name.
        """
        try:
            from model_old_schema.feature import Feature
            session = self.SessionFactory()
            f = session.query(Feature).filter(Feature.name == name.upper()).first()
            if f:
                return f
            return session.query(Feature).filter(Feature.gene_name == name.upper()).first();
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
    
    def get_reftemp_by_pmid(self, pubmed_id):
        """
        Get a reftemp by its pubmed_id.
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
            
    def get_refbad_by_pmid(self, pubmed_id):
        """
        Get a refbad by its pubmed_id.
        """
        try:
            from model_old_schema.reference import RefBad
            session = self.SessionFactory()
            pubmed_id_as_int = int(float(pubmed_id))
            return session.query(RefBad).filter_by(pubmed_id=pubmed_id_as_int).first();
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
            
    def get_ref_by_pmid(self, pubmed_id, session_a=None):
        """
        Get a reference by its pubmed_id.
        """
        try:
            from model_old_schema.reference import Reference
            if session_a is None:
                session = self.SessionFactory()
            else:
                session = session_a
            pubmed_id_as_int = int(float(pubmed_id))
            return session.query(Reference).filter_by(pubmed_id=pubmed_id_as_int).first();
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            if session_a is None:
                session.close()
    
    def get_reftemps(self):
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
    
    def move_reftemp_to_refbad(self, pubmed_id):
        """"
        Remove reference from the RefTemp table and add it to the RefBad table.
        """
        try:       
            from model_old_schema.reference import RefBad
            session = self.SessionFactory()
            reftemp = self.get_reftemp_by_pmid(pubmed_id)
            refbad = RefBad(pubmed_id)
            session.add(refbad)
            session.delete(reftemp)
            session.commit()
            return True
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            session.close()
            
    def move_refbad_to_reftemp(self, pubmed_id):
        """"
        Remove reference from the RefBad table and add it to the RefTemp table.
        """
        try:       
            from model_old_schema.reference import RefTemp
            session = self.SessionFactory()
            
            refbad = self.get_refbad_by_pmid(pubmed_id)
            pubmed = self.get_medline_data(pubmed_id)
            reftemp = RefTemp(pubmed_id, pubmed.citation, None, pubmed.abstract_txt)
            
            session.add(reftemp)
            session.delete(refbad)
            session.commit()
            return True
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
            return False
        finally:
            session.close()
            
    def move_reftemp_to_ref(self, pubmed_id):
        """
        Remove reference from the RefTemp table, create a full Reference, and add it to the Reference table.
        """
        try:       
            session = self.SessionFactory()
            reftemp = self.get_reftemp_by_pmid(pubmed_id)
            ref = self.create_reference(pubmed_id)
            
            session.add(ref)
            session.delete(reftemp)
            session.commit()
            return True
        except:
            return False
            session.rollback()
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
            
    def move_ref_to_reftemp(self, pubmed_id):
        """
        Remove reference from the Reference table and add it to the RefTemp table.
        """
        try:  
            from model_old_schema.reference import RefTemp     
            session = self.SessionFactory()
            ref = self.get_ref_by_pmid(pubmed_id)
            reftemp = RefTemp(pubmed_id, ref.citation, None, ref.abstract)
            
            session.add(reftemp)
            session.delete(ref)
            session.commit()
            return True
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
            
    def validate_genes(self, gene_names):
        """
        Convert a list of gene_names to a mapping between those gene_names and features.
        """
        try:
            from model_old_schema.feature import Feature
            session = self.SessionFactory()
            
            if gene_names is not None and len(gene_names) > 0:
                upper_gene_names = [x.upper() for x in gene_names]
                fs = set(session.query(Feature).filter(Feature.name.in_(upper_gene_names)).all())
                fs.update(session.query(Feature).filter(Feature.gene_name.in_(upper_gene_names)).all())
            
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
            else:
                return {}
        except:
            return False
            session.rollback()
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
            
    def get_medline_data(self, pubmed_id):
        """
        Grab information on this pubmed_id from ncbi using FetchMedline()
        """
        medline = FetchMedline(pubmed_id)
        records = medline.get_records()
        for rec in records:
            record = rec
        return Pubmed(record)
            
    def create_reference(self, pubmed_id):
        """
        Create a Reference from a RefTemp. First grab information on the Reference from NCBI.
        Then create the reference with its associated object: Journal, Abstract, Author, RefType.
        """
        try:            
            session = self.SessionFactory()

            #Check if reference already exists.
            from model_old_schema.reference import Reference, Journal, Author, RefType
            ref = get_or_create(session, Reference, pubmed_id=pubmed_id)
            
            pubmed = self.get_medline_data(pubmed_id)
            
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
            ref.abstract = pubmed.abstract_txt
                    
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
        finally:
            session.close()
            
    def associate(self, pubmed_id, name_to_feature, tasks):
        """
        Associate a Reference with LitGuide entries.
        """
        try:
            from model_old_schema.admin import RefCuration
            from model_old_schema.reference import LitGuide
            session = self.SessionFactory()
                        
            reference = self.get_ref_by_pmid(pubmed_id, session)
            
            for task in tasks:
                
                
                gene_names = task.gene_names
                if gene_names is not None and len(gene_names) > 0:
                    #Convert gene_names to features using the name_to_feature table.                
                    features = set()
                    for gene_name in task.gene_names:
                        features.add(name_to_feature[gene_name])
                    
                    ## Create RefCuration objects and add them to the Reference.
                    for feature in features:
                        curation = get_or_create(session, RefCuration, reference_id = reference.id, task = task.name, feature_id = feature.id)
                        curation.comment = task.comment
                        reference.curations.append(curation)
                            
                    ## Create a LitGuide object and attach features to it.
                    lit_guide = get_or_create(session, LitGuide, topic=task.topic)
                    for feature in features:
                        if not feature.id in lit_guide.feature_ids:
                            lit_guide.features.append(feature)
                    reference.litGuides.append(lit_guide)

                    
                else:   ## no gene name provided

                    ## if no gene name provided and "Add to database" was checked,
                    ## no need to add any association
                    if task.type == TaskType.ADD_TO_DATABASE:
                        continue

                    ## if it is a review, no need to add to ref_curation
                    if task.type == TaskType.REVIEWS:
                        ## topic = task = 'Reviews'
                        reference.litGuideTopics.append(task.topic)

                    curation = get_or_create(session, RefCuration, task=task.name, reference_id = reference.id, feature_id=None)
                    curation.comment = task.comment
                    reference.curations.append(curation)
            
                    ## Create a LitGuide object.
                    if task.type == TaskType.HTP_PHENOTYPE_DATA or task.type == TaskType.REVIEWS:
                        lit_guide = get_or_create(session, LitGuide, topic=task.topic, reference_id=reference.id)
                        reference.litGuides.append(lit_guide)
            session.commit()
            return True
        except Exception:
            traceback.print_exc(file=sys.stdout)
            session.rollback()
            return False
        finally:
            session.close()
            
    def get_curations_for_ref(self, pubmed_id):
        """
        Get curations for the reference with this pubmed_id
        """
        try:  
            session = self.SessionFactory()
            ref = self.get_ref_by_pmid(pubmed_id, session)
            curations = ref.curations
            return curations
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()
            
    def get_lit_guides_for_ref(self, pubmed_id):
        """
        Get lit review topics for the reference with this pubmed_id
        """
        try:  
            session = self.SessionFactory()
            ref = self.get_ref_by_pmid(pubmed_id, session)
            litGuidess = ref.litGuides
            return litGuidess
        except:
            session.rollback()
            traceback.print_exc(file=sys.stdout)
        finally:
            session.close()


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
    #r = conn.getRefTempByPmid(23079598)
    #result = conn.moveRefTempToReference(23079598)
    #print result
    result = conn.get_reftemps()
    
    