import unittest
from pathlib import Path
class DemoTests(unittest.TestCase):
    def test_source_exists(self): self.assertTrue(Path('src/message.txt').exists())
if __name__=='__main__':unittest.main()
