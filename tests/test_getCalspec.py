import unittest
from getCalspec import is_calspec, Calspec
from astropy.table import Table as astropyTable


class GetCalspecTestCase(unittest.TestCase):
    """A test case for the defect finding task."""

    def test_is_calspec(self):
        self.assertTrue(is_calspec("eta1 dor"))
        self.assertFalse(is_calspec("NotACalspecStar"))
        self.assertFalse(is_calspec("Not A Calspec Star With Spaces"))

    def test_Calspec(self):
        c = Calspec('eta dor')
        table = c.get_spectrum_table()
        self.assertIsInstance(table, astropyTable)


if __name__ == "__main__":
    unittest.main()
