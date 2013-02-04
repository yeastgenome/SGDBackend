
from model_old_schema.model import Model, get_first, get, count
from unittest.suite import TestSuite
from webapp.config import DBTYPE, DBHOST, DBNAME, SCHEMA
import unittest


class ModelCreationMixin(unittest.TestCase):
    def setUp(self):
        self.model = Model(DBTYPE, DBHOST, DBNAME, SCHEMA)
        #self.model.connect(DBUSER, DBPASS)

class TestConnection(ModelCreationMixin):
    
    def test_is_connected(self):
        self.assertTrue(self.model.is_connected())
        
def test_validity(test, obj, obj_validation_method, session=None, **kwargs):
    def f(session):
        obj_from_session = obj(session=session)
        obj_validation_method(test, obj_from_session, **kwargs)
    return f if session is None else f(session)
        
def validate_ref(test, ref, pubmed_id=None, ref_id=None):
    test.assertTrue(ref is not None)
    test.assertTrue(ref.id is not None)
    test.assertTrue(ref.pubmed_id is not None)
    test.assertTrue(ref.abstract is not None)
    test.assertTrue(ref.journal is not None)
    test.assertTrue(ref.created_by is not None)
    test.assertTrue(ref.date_created is not None)
    
    if pubmed_id is not None:
        test.assertEqual(ref.pubmed_id, pubmed_id)
    if ref_id is not None:
        test.assertEqual(ref.id, ref_id)

def validate_reftemp(test, reftemp, pubmed_id=None, reftemp_id=None):
    test.assertTrue(reftemp is not None)
    test.assertTrue(reftemp.id is not None)
    test.assertTrue(reftemp.pubmed_id is not None)
    test.assertTrue(reftemp.citation is not None)
    test.assertTrue(reftemp.abstract is not None)
    test.assertTrue(reftemp.created_by is not None)
    test.assertTrue(reftemp.date_created is not None)
    
    if pubmed_id is not None:
        test.assertEqual(reftemp.pubmed_id, pubmed_id)
    if reftemp_id is not None:
        test.assertEqual(reftemp.id, reftemp_id)
        
def validate_refbad(test, refbad, pubmed_id=None):    
    test.assertTrue(refbad is not None)
    test.assertTrue(refbad.pubmed_id is not None)
    test.assertTrue(refbad.created_by is not None)
    test.assertTrue(refbad.date_created is not None)
    
    if pubmed_id is not None:
        test.assertEqual(refbad.pubmed_id, pubmed_id)

def validate_feature(test, feature, feature_id=None, feature_name=None):    
    test.assertTrue(feature is not None)
    test.assertTrue(feature.id is not None)
    test.assertTrue(feature.name is not None)
    test.assertTrue(feature.created_by is not None)
    test.assertTrue(feature.date_created is not None)
    
    if feature_id is not None:
        test.assertEqual(feature.id, feature_id)
    if feature_name is not None:
        test.assertEqual(feature.name.upper(), feature_name.upper())

class TestGetFeaturesAndReferences(ModelCreationMixin):
        
    def test_get_reftemps(self):
        from model_old_schema.reference import RefTemp
        refs = self.model.execute(get(RefTemp))
        self.assertTrue(len(refs) > 0)
        
    def test_get_feature(self, feature_id=1971, feature_name='yjl001W'):
        from model_old_schema.feature import Feature
        f = get_first(Feature, id=feature_id)
        self.model.execute(test_validity(self, f, validate_feature, feature_id=feature_id, feature_name=feature_name))
        
    def test_get_reftemp(self, reftemp_id=81007, pubmed_id=23125886):
        from model_old_schema.reference import RefTemp
        reftemp = get_first(RefTemp, id=reftemp_id)
        self.model.execute(test_validity(self, reftemp, validate_reftemp, reftemp_id=reftemp_id, pubmed_id=pubmed_id))
    
    def test_get_refbad(self, pubmed_id=16998476):
        from model_old_schema.reference import RefBad
        refbad = get_first(RefBad, pubmed_id=pubmed_id)
        self.model.execute(test_validity(self, refbad, validate_refbad, pubmed_id=pubmed_id))
            
    def test_get_ref(self, pubmed_id=1986222, ref_id=84):
        from model_old_schema.reference import Reference
        ref = get_first(Reference, id=ref_id)
        self.model.execute(test_validity(self, ref, validate_ref, ref_id=ref_id))
                
    def test_count_refs(self):
        from model_old_schema.reference import Reference
        ref_count = self.model.execute(count(Reference))
        self.assertTrue(ref_count > 0)
            
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestGetFeaturesAndReferences('test_get_references'))
    unittest.TextTestRunner().run(suite)
    
