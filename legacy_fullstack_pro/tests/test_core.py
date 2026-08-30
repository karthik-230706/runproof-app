import unittest, tempfile, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from core.engine import analyze_project
from core.dependency_checker import analyze_dependencies

class CoreTests(unittest.TestCase):
    def test_dependency_pinning(self):
        d=analyze_dependencies(ROOT/'demo/good_project','Python')
        self.assertEqual(d['unpinned'],0)
    def test_good_static(self):
        a,_,_,_=analyze_project(ROOT/'demo/good_project','static',20,False,'test-secret')
        self.assertEqual(a['detection']['type'],'Python')
        self.assertGreaterEqual(a['score']['score'],70)
    def test_good_verify(self):
        a,_,_,_=analyze_project(ROOT/'demo/good_project','trusted',20,True,'test-secret')
        self.assertTrue(a['verification']['verified'])
    def test_nonrepro(self):
        a,_,_,_=analyze_project(ROOT/'demo/non_reproducible_project','trusted',20,True,'test-secret')
        self.assertEqual(a['verification']['status'],'mismatch')
if __name__=='__main__':unittest.main()
