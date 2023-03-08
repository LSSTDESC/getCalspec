import unittest
from getCalspec import is_calspec, Calspec
from astropy.table import Table as astropyTable


class GetCalspecTestCase(unittest.TestCase):
    """A test case for the getCalspec package."""

    def test_is_calspec(self):
        self.assertTrue(is_calspec("eta1 dor"))
        self.assertFalse(is_calspec("NotACalspecStar"))
        self.assertFalse(is_calspec("Not A Calspec Star With Spaces"))

    def test_Calspec(self):
        c = Calspec('eta dor')
        table = c.get_spectrum_table()
        self.assertIsInstance(table, astropyTable)

        data = c.get_spectrum_numpy()
        self.assertIsInstance(data, dict)
        expectedKeys = ['WAVELENGTH', 'FLUX', 'STATERROR', 'SYSERROR']
        for key in expectedKeys:
            self.assertIn(key, data.keys())


if __name__ == "__main__":
    unittest.main()
