import os
import unittest
import utils

import helper

class FindRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = utils._FindRule()

    def test_call(self):
        try:
            self.rule(None, None)
        except NotImplementedError:
            pass

    def test_render(self):
        self.assertTrue(self.rule.render())
        self.assertFalse(self.rule.render(False))
        rule = utils._FindRule(exclude=True)
        self.assertFalse(rule.render())
        self.assertTrue(rule.render(False))

class FindDirectoryRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = utils._FindDirectoryRule(True)

    def test_call(self):
        file_path = os.path.realpath(__file__)
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        dir_name = os.path.basename(dir_path)
        self.assertFalse(self.rule(file_name, utils.stat(file_path)))
        self.assertTrue(self.rule(dir_name, utils.stat(dir_path)))

class FindFileRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = utils._FindFileRule(True)

    def test_call(self):
        file_path = os.path.realpath(__file__)
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        dir_name = os.path.basename(dir_path)
        self.assertTrue(self.rule(file_name, utils.stat(file_path)))
        self.assertFalse(self.rule(dir_name, utils.stat(dir_path)))

class FindFileRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = utils._FindNameRule('*hello[12].py?')

    def test_call(self):
        self.assertTrue(self.rule('hello1.pyc', None))
        self.assertTrue(self.rule('test-hello2.pyo', None))
        self.assertFalse(self.rule('world.py', None))

if __name__ == '__main__':
    unittest.main()
