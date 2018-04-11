from .context import zipaspng
import os
import unittest


class TestDisguiseFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_disguise_file(self):
        here = os.path.dirname(__file__)
        with open(os.path.join(here, "assets", "hoge.zip"), "rb") as zip, \
             open(os.path.join(here, "assets", "test.png"), "rb") as png, \
             open(os.path.join(here, "assets", "output.zip.png"), "rb") as expect:
           zip_data = zip.read()
           png_data = png.read()
           out_data = zipaspng.disguise(zip_data, png_data)
           expect_data = expect.read()
           assert out_data == expect_data

if __name__ == '__main__':
    unittest.main()
