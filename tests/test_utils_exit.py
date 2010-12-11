import helper

import StringIO
import sys
import unittest
import ops.utils

class ExitTestCase(unittest.TestCase):

    def setUp(self):
        self.real_stdout = sys.stdout
        self.real_stderr = sys.stderr
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.real_stdout
        sys.stderr = self.real_stderr

    def test_code(self):
        self.assertRaises(SystemExit, ops.utils.exit, code=0)
        self.assertRaises(SystemExit, ops.utils.exit, code=1)
        try:
            ops.utils.exit(code=1)
        except SystemExit, exit:
            self.assertEqual(exit.code, 1)

    def test_stdout(self):
        try:
            ops.utils.exit(text='Successfuly')
        except SystemExit:
            pass
        result = sys.stdout.getvalue().rstrip()
        self.assertEqual(result, 'Successfuly')

    def test_stderr(self):
        try:
            ops.utils.exit(code=1, text='Failure')
        except SystemExit:
            pass
        result = sys.stderr.getvalue().rstrip()
        self.assertEqual(result, 'Failure')

if __name__ == '__main__':
    unittest.main()
