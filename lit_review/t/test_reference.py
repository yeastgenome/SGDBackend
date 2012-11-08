import unittest
import sys
# how to set the relative path??
sys.path.append('/home/shuai/sgd2/curation/')
from reference.models import *

class TestRefTemp(unittest.TestCase):

    # initialize - run before any tests
    def setUp(self):
        refs = RefTemp.search()
        self.num_of_refs = len(refs.all())
        self.pmid = refs.first().pubmed
        
    # clean up - run after all tests
    # def tearDown(self):

    def test_delete(self):
        RefTemp.delete(self.pmid)
        db.session.commit()
        refs = RefTemp.search()
        self.assertEqual(len(refs.all()), self.num_of_refs - 1)

        refs = RefTemp.search(self.pmid)
        self.assertEqual(refs.first(), None)

class TestRefBad(unittest.TestCase):

    def setUp(self):
        refs = RefTemp.search()
        self.pmid = refs.first().pubmed

    def test_insert(self):
        RefBad.insert(self.pmid)
        db.session.commit()
        self.refbad_query = RefBad.query.filter_by(pubmed=self.pmid)
        self.assertEqual(self.refbad_query.first().pubmed, self.pmid)
        
    def tearDown(self):
        self.refbad_query.delete()
        db.session.commit()

class TestReference(unittest.TestCase):

    def setUp(self):
        refs = RefTemp.search()
        row = refs.first()
        self.pmid = row.pubmed
        self.citation = row.citation
        self.abstract = row.abstract
        self.topic = 'Comprehensive set'
        self.task = 'GO curation'
        self.feature_no = 4430
        
    def test_insert(self):

        ## Reference and related tables 
        ref_no = Reference.insert(self.pmid)
        self.ref_query = Reference.query.filter_by(reference_no=ref_no)
        self.assertTrue(self.ref_query.first())
        self.assertEqual(self.ref_query.first().pubmed, self.pmid)
        self.assertEqual(self.ref_query.first().citation, self.citation)

        ## lit_guide table
        litguide_no = LitGuide.insert(ref_no, self.topic)
        litguide_query = LitGuide.query.filter_by(lit_guide_no=litguide_no)
        self.assertEqual(litguide_query.first().literature_topic, self.topic)
        self.assertEqual(litguide_query.first().reference_no, ref_no)

        ## litguide_feat table
        lgfeat_query = LitGuideFeat.insert(self.feature_no, litguide_no)
        db.session.commit()
        lg_query = LitGuideFeat.query.filter_by(feature_no=self.feature_no,
                                                lit_guide_no=litguide_no)
        self.assertTrue(lg_query.first())
        
        ## ref_curation table
        RefCuration.insert(ref_no, self.task, self.feature_no)
        db.session.commit();
        rc_query = RefCuration.query.filter_by(reference_no=ref_no,
                                               curation_task=self.task,
                                               feature_no=self.feature_no)
        feat_no = rc_query.first().feature_no
        self.assertEqual(feat_no, self.feature_no)
        
    def tearDown(self):
        self.ref_query.delete()
        db.session.commit()


        
if __name__ == '__main__':
    unittest.main()
    
