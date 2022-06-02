import unittest
from getCalspec import is_calspec


class GetCalspecTestCase(unittest.TestCase):
    """A test case for the defect finding task."""

    def testInit(self):
        self.assertTrue(is_calspec("eta1 dor"))
        self.assertFalse(is_calspec("NotACalspecStar"))
        self.assertFalse(is_calspec("Not A Calspec Star With Spaces"))
