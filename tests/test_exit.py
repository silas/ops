import StringIO
import sys
import unittest
import opsutils

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
        self.assertRaises(SystemExit, opsutils.exit, code=0)
        self.assertRaises(SystemExit, opsutils.exit, code=1)
        try:
            opsutils.exit(code=1)
        except SystemExit, exit:
            self.assertEqual(exit.code, 1)

    def test_stdout(self):
        try:
            opsutils.exit(text='Successfuly')
        except SystemExit:
            pass
        result = sys.stdout.getvalue().rstrip()
        self.assertEqual(result, 'Successfuly')

    def test_stderr(self):
        try:
            opsutils.exit(code=1, text='Failure')
        except SystemExit:
            pass
        result = sys.stderr.getvalue().rstrip()
        self.assertEqual(result, 'Failure')

if __name__ == '__main__':
    unittest.main()
