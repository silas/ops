from __future__ import unicode_literals

import helper

import os
import unittest

import ops

PATH = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))


class PathTestCase(unittest.TestCase):

    def setUp(self):
        self.path = ops.path(PATH)

    def test_join(self):
        self.assertEqual(self.path.join('tests'), '%s/tests' % PATH)

    def test_stat(self):
        self.assertTrue(isinstance(self.path.stat, ops.stat))

    def test_type(self):
        self.assertTrue(isinstance(self.path, helper.unicode_type))


if __name__ == '__main__':
    unittest.main()
