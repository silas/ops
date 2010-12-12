import helper

import os
import unittest
import uuid
import ops.utils

class RunTestCase(unittest.TestCase):

    def setUp(self):
        self.root_path = os.path.dirname(os.path.realpath(__file__))
        self.run_path = os.path.join(self.root_path, 'assets', 'run.py')

    def do(self, text='', code=0):
        r = ops.utils.run('python ${run} ${code} ${text}',
            run=self.run_path,
            code=code,
            text=text,
        )
        return r

    def text(self):
        return '"some uuid" \' *>/ %s' % uuid.uuid4().get_hex()

    def test_successful(self):
        text = self.text()
        results = self.do(text=text)
        self.assertTrue(results)
        self.assertEqual(results.stdout, 'stdout: %s' % text)
        self.assertEqual(results.stderr, 'stderr: %s' % text)

    def test_failure(self):
        text = self.text()
        results = self.do(code=5, text=text)
        self.assertFalse(results)
        self.assertEqual(results.stdout, 'stdout: %s' % text)
        self.assertEqual(results.stderr, 'stderr: %s' % text)

    def test_dict(self):
        args = {'-f': self.run_path}
        results = ops.utils.run('test ${args}', args=args)
        self.assertTrue(results)
        self.assertEqual(results.code, 0)
        print results.command

    def test_list(self):
        args = ['?!*', '=', '?!*']
        results = ops.utils.run('test ${args}', args=args)
        self.assertTrue(results)
        self.assertEqual(results.code, 0)

if __name__ == '__main__':
    unittest.main()
