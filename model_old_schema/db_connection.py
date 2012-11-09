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
                ref = Reference(pubmed.publish_status, pubmed.citation, pubmed.year, pubmed_id,
                             'PubMed script', pubmed.pdf_status, pubmed.pages, pubmed.volume,
                             pubmed.title, pubmed.issue)
                
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
            
    def associate(self, reference, name_to_feature, tasks):
        """
        Associate a Reference with LitGuide entries.
        """
        try:
            from model_old_schema.admin import RefCuration
            session = self.SessionFactory()
            
            message = ''
            topic_added = {}
            task_added = {}
        

            if len(tasks) == 0:
                return None

            for task_entry in tasks:
                task = task_entry[0]    
                genes = task_entry[1]
                comment = task_entry[2]
            
                if len(genes) > 0:
                    feature_list = []
            
                    topic = ''
                    if 'Add to' in task:
                        topic = 'Additional Literature'
                    elif 'Review' in task:
                        topic = task
                    else:
                        topic = 'Primary Literature'
            
                    if 'Review' in task or 'Add to' in task:
                        task = 'Gene Link'

                        message += "Curation_task = '" + task
                        message += "', literature_topic = '" + topic + "'"
                        message += ", gene = "
                 
                    for name in genes:
                        feature = name_to_feature[name.upper()]
                        feature_id = feature.id
                        feature_list.append(feature)
                        
                        ## Create RefCuration objects and add them to the Reference.
                        if not task_added.has_key((feature_id, task)):
                            curation = reference.curation.filter_by(task=task, feature_id=feature_id)
                            if not curation:
                                curation = RefCuration(task, feature_id, comment)
                                reference.curation.append(curation)
                                task_added[(feature_id, task)] = 1
                            message += name + '|'

                    if comment:
                        message += ", comment = '" + comment + "'"
                    
                    message += "<br>"
            
                    ## insert into lit_guide + litguide_feat
            
                    if topic_added.has_key(topic):
                        lit_guide = topic_added[topic]
                    else:
                        reference.litReviewTopics.append(topic)
                        lit_guide = reference.litReviewTopics.last()
                        topic_added[topic] = lit_guide
            
                    feature_ids_added = set()
                    for feature in feature_list:
                        feature_id = feature.id
                        if feature_id in feature_ids_added:
                            continue
                        feature_ids_added.add(feature_id)
                        lit_guide.features.append(feature)
                    
                else:   ## no gene name provided

                    ## if no gene name provided and "Add to database" was checked,
                    ## no need to add any association
                    if 'Add' in task:
                        continue

                    ## if it is a review, no need to add to ref_curation
                    if 'Review' in task:
                        ## topic = task = 'Reviews'
                        reference.litReviewTopics.append(topic)
                        message += "Literature_topic = '" + task + "'<br>"
                        continue

                    if not task_added.has_key((0, task)):
                        curation = RefCuration(task, None, comment)
                        reference.curation.append(curation)
                        task_added[(0, task)] = 1
                
                        message += "Curation_task = '" + task + "'"
            
                    ## insert into lit_guide 
                    if 'HTP' in task or 'Review' in task:

                        topic = ''
                        if 'HTP' in task:
                            topic = 'Omics'
                        else:
                            # 'Review' in task:
                            topic = task
                    
                        if topic_added.has_key(topic):
                            if comment:
                                message += ", comment = '" + comment + "'"
                                message += "<br>"
                                continue
                            else:    
                                reference.litReviewTopics.append(topic)
                                lit_guide = reference.litReviewTopics.last()
                                topic_added[topic] = lit_guide
                            message += ", literature_topic = '" + topic

                    if comment:
                        message += ", comment = '" + comment + "'"
                    
                    message += "<br>"
                
                session.commit()
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
     
if __name__ == '__main__':
    conn = DBConnection()
    conn.connect(DBUSER, DBPASS)
    #r = conn.getRefTempByPmid(23118484)
    #print conn.moveRefTempToReference(22888114)
    #print r
    #result = conn.createReference(r)
    #print result
    r = conn.getReferenceByID(64810)
    print r
    print r.curations
    
    