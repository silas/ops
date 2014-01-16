from __future__ import unicode_literals

import helper

import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import ops


class ExitTestCase(unittest.TestCase):

    def setUp(self):
        self.real_stdout = sys.stdout
        self.real_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.real_stdout
        sys.stderr = self.real_stderr

    def test_code(self):
        self.assertRaises(SystemExit, ops.exit, code=0)
        self.assertRaises(SystemExit, ops.exit, code=1)
        try:
            ops.exit(code=1)
        except SystemExit as exit:
            self.assertEqual(exit.code, 1)

    def test_stdout(self):
        try:
            ops.exit(text='Successfuly')
        except SystemExit:
            pass
        result = sys.stdout.getvalue().rstrip()
        self.assertEqual(result, 'Successfuly')

    def test_stderr(self):
        try:
            ops.exit(code=1, text=False)
        except SystemExit:
            pass
        result = sys.stderr.getvalue().rstrip()
        self.assertEqual(result, 'False')

if __name__ == '__main__':
    unittest.main()
