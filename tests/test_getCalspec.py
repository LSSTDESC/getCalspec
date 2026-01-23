import unittest
from getCalspec import is_calspec, Calspec
from astropy.io.fits import FITS_rec
import astropy
import os


class GetCalspecTestCase(unittest.TestCase):
    """A test case for the getCalspec package."""

    def test_is_calspec(self):
        self.assertTrue(is_calspec("BD+54 1216"))
        self.assertTrue(is_calspec("eta1 dor"))
        self.assertFalse(is_calspec("NotACalspecStar"))
        self.assertFalse(is_calspec("Not A Calspec Star With Spaces"))

    @astropy.config.set_temp_cache(os.path.join(os.path.abspath(os.path.dirname(__file__)), "data", "cache"))
    def test_Calspec(self):
        c = Calspec("eta dor")
        table = c.get_spectrum_table()
        self.assertIsInstance(table, FITS_rec)

        data = c.get_spectrum_numpy()
        self.assertIsInstance(data, dict)
        expectedKeys = ["WAVELENGTH", "FLUX", "STATERROR", "SYSERROR"]
        for key in expectedKeys:
            self.assertIn(key, data.keys())


if __name__ == "__main__":
    unittest.main()
