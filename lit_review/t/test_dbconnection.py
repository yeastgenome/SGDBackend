from lit_review.parse import Task, TaskType
from model_old_schema.config import DBUSER, DBPASS
from model_old_schema.db_connection import DBConnection
from unittest.suite import TestSuite
import unittest

class TestConnection(unittest.TestCase):
    
    def test_is_connected(self):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        self.assertTrue(conn.is_connected())
        

class TestGetAndMoveFeaturesAndReferences(unittest.TestCase):
        
    def test_get_feature_by_name_basic(self, feature_name='YJL001W', feature_id=1971):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        f = conn.get_feature_by_name(feature_name)
        self.assertEqual(f.id, feature_id)
        
    def test_get_feature_by_name_case(self):
        feature_name = 'yjl001W'
        feature_id = 1971
        self.test_get_feature_by_name_basic(feature_name, feature_id)
        
    def test_get_feature_by_name_genename(self):
        gene_name = 'PRE3'
        feature_id = 1971
        self.test_get_feature_by_name_basic(gene_name, feature_id)
    
    def test_get_reftemp_by_pmid(self, pubmed_id=23091010, reftemp_id=80816):
        self.valid_reftemp(pubmed_id, reftemp_id)
    
    def test_get_refbad_by_pmid(self, pubmed_id=16830189):
        self.valid_refbad(pubmed_id)
    
    def test_get_ref_by_pmid(self, pubmed_id=1986222, ref_id=84):
        self.valid_ref(pubmed_id, ref_id)
        
    def test_get_reftemps(self):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        rs = conn.get_reftemps()
        self.assertTrue(len(rs) > 0)
        
    def test_move_refbad_to_reftemp(self, pubmed_id=16830189):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        try:
            result = conn.move_refbad_to_reftemp(pubmed_id)
            self.assertTrue(result)
            self.valid_reftemp(pubmed_id)
        finally:
            conn.move_reftemp_to_refbad(pubmed_id)
        
    def test_move_reftemp_to_refbad(self, pubmed_id=23080253):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        try:

            result = conn.move_reftemp_to_refbad(pubmed_id)
            self.assertTrue(result)
            self.valid_refbad(pubmed_id)
        finally:
            conn.move_refbad_to_reftemp(pubmed_id)
        
    def test_move_reftemp_to_ref(self, pubmed_id=22416066):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        try:
            result = conn.move_reftemp_to_ref(pubmed_id)
            self.assertTrue(result)
            self.valid_ref(pubmed_id)
        finally:
            conn.move_ref_to_reftemp(pubmed_id)
            
    def test_move_ref_to_reftemp(self, pubmed_id=10783002):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        try:
            result = conn.move_ref_to_reftemp(pubmed_id)
            self.assertTrue(result)
            self.valid_reftemp(pubmed_id)
        finally:
            conn.move_reftemp_to_ref(pubmed_id)
            
    def valid_ref(self, pubmed_id, ref_id=None):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        ref = conn.get_ref_by_pmid(pubmed_id)
        
        self.assertTrue(ref.abstract is not None)
        self.assertTrue(ref.journal is not None)
        self.assertTrue(ref.created_by is not None)
        self.assertTrue(ref.date_created is not None)
        
        self.assertEqual(ref.pubmed_id, pubmed_id)
        if ref_id is not None:
            self.assertEqual(ref.id, ref_id)
            
    def valid_reftemp(self, pubmed_id, reftemp_id=None):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        reftemp = conn.get_reftemp_by_pmid(pubmed_id)
        
        self.assertTrue(reftemp.citation is not None)
        self.assertTrue(reftemp.abstract is not None)
        self.assertTrue(reftemp.created_by is not None)
        self.assertTrue(reftemp.date_created is not None)
        
        self.assertEqual(reftemp.pubmed_id, pubmed_id)
        if reftemp_id is not None:
            self.assertEqual(reftemp.id, reftemp_id)
            
    def valid_refbad(self, pubmed_id):
        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        refbad = conn.get_refbad_by_pmid(pubmed_id)
        
        self.assertTrue(refbad.created_by is not None)
        self.assertTrue(refbad.date_created is not None)
        
        self.assertEqual(refbad.pubmed_id, pubmed_id)
            
class TestAssociate(unittest.TestCase):
    
    def test_validate_genes(self):
        gene_names = ['YAL002W', 'CEN1', 'SPO7', 'YAL016C-B', 'YAL009W']
        feature_ids = [6102, 2899, 6347, 7398, 6347]

        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        name_to_feature = conn.validate_genes(gene_names)
        
        self.assertEqual(len(gene_names), len(name_to_feature))
        for i in range(0, len(gene_names)):
            self.assertEqual(name_to_feature[gene_names[i]].id, feature_ids[i])
            
    def test_associate(self):
        pubmed_id = 23103252
        gene_names = ['YAL002W', 'CEN1', 'SPO7', 'YAL016C-B', 'YAL009W']

        conn = DBConnection()
        conn.connect(DBUSER, DBPASS)
        try:
            conn.move_reftemp_to_ref(pubmed_id)
            name_to_feature = conn.validate_genes(gene_names)
            tasks = [#Task(TaskType.HIGH_PRIORITY, None, None),
                     #Task(TaskType.DELAY, None, None),
                     #Task(TaskType.HTP_PHENOTYPE_DATA, None, None),
                     #Task(TaskType.OTHER_HTP_DATA, None, None),
                     Task(TaskType.CLASSICAL_PHENOTYPE_INFORMATION, ['YAL002W'], None)]
            
            result = conn.associate(pubmed_id, name_to_feature, tasks)
            self.assertTrue(result)
            
            print conn.get_curations_for_ref(pubmed_id)
            print conn.get_lit_guides_for_ref(pubmed_id)
        finally:
            conn.move_ref_to_reftemp(pubmed_id)
        
        
if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(TestAssociate('test_associate'))
    unittest.TextTestRunner().run(suite)
    
