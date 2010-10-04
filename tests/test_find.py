import helper

import datetime
import copy
import os
import unittest
import opsutils

class FindRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = opsutils._FindRule()

    def test_call(self):
        try:
            self.rule(None, None)
        except NotImplementedError:
            pass

    def test_render(self):
        self.assertTrue(self.rule.render())
        self.assertFalse(self.rule.render(False))
        rule = opsutils._FindRule(exclude=True)
        self.assertFalse(rule.render())
        self.assertTrue(rule.render(False))

class FindDirectoryRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = opsutils._FindDirectoryRule(True)
        self.file_path = os.path.realpath(__file__)

    def test_call(self):
        name = os.path.basename(self.file_path)
        self.assertFalse(self.rule(name, opsutils.stat(self.file_path)))

    def test_directory(self):
        path = os.path.dirname(self.file_path)
        name = os.path.basename(path)
        self.assertTrue(self.rule(name, opsutils.stat(path)))

class FindFileRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = opsutils._FindFileRule(True)
        self.file_path = os.path.realpath(__file__)

    def test_file(self):
        name = os.path.basename(self.file_path)
        self.assertTrue(self.rule(name, opsutils.stat(self.file_path)))

    def test_directory(self):
        path = os.path.dirname(self.file_path)
        name = os.path.basename(path)
        self.assertFalse(self.rule(name, opsutils.stat(path)))

class FindNameRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = opsutils._FindNameRule('*hello[12].py?')

    def test_match(self):
        self.assertTrue(self.rule('hello1.pyc', None))
        self.assertTrue(self.rule('test-hello2.pyo', None))

    def test_no_match(self):
        self.assertFalse(self.rule('world.py', None))

class FindTimeRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.dt_eq = datetime.datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15)
        self.dt_lt = datetime.datetime(year=2001, month=1, day=2, hour=3, minute=4, second=5)
        self.dt_gt = datetime.datetime(year=2021, month=2, day=3, hour=4, minute=5, second=6)
        self.stat = opsutils.objectify({'ctime': copy.deepcopy(self.dt_eq)})

    def rule(self, o, v, type='ctime'):
        return opsutils._FindTimeRule(type, o, v)(None, self.stat)

    def test_exact(self):
        self.assertTrue(self.rule('', self.dt_eq))
        self.assertTrue(self.rule('exact', self.dt_eq))
        self.assertFalse(self.rule('', self.dt_lt))
        self.assertFalse(self.rule('exact', self.dt_lt))

    def test_lt(self):
        self.assertTrue(self.rule('lt', self.dt_gt))
        self.assertFalse(self.rule('lt', self.dt_lt))

    def test_lte(self):
        self.assertTrue(self.rule('lte', self.dt_gt))
        self.assertTrue(self.rule('lte', self.dt_eq))
        self.assertFalse(self.rule('lte', self.dt_lt))

    def test_gt(self):
        self.assertTrue(self.rule('gt', self.dt_lt))
        self.assertFalse(self.rule('gt', self.dt_gt))

    def test_gte(self):
        self.assertTrue(self.rule('gte', self.dt_lt))
        self.assertTrue(self.rule('gte', self.dt_eq))
        self.assertFalse(self.rule('gte', self.dt_gt))

    def test_year(self):
        self.assertTrue(self.rule('year', 2010))
        self.assertFalse(self.rule('year', 2000))

    def test_month(self):
        self.assertTrue(self.rule('month', 11))
        self.assertFalse(self.rule('month', 1))

    def test_day(self):
        self.assertTrue(self.rule('day', 12))
        self.assertFalse(self.rule('day', 1))

    def test_hour(self):
        self.assertTrue(self.rule('hour', 13))
        self.assertFalse(self.rule('hour', 1))

    def test_minute(self):
        self.assertTrue(self.rule('minute', 14))
        self.assertFalse(self.rule('minute', 1))

    def test_second(self):
        self.assertTrue(self.rule('second', 15))
        self.assertFalse(self.rule('second', 1))

class FindTestCase(unittest.TestCase):

    def test_add_rule_name(self):
        find = opsutils.find('.')
        find._add_rule({'name': '*.pyc'})
        self.assertEqual(len(find.rules), 1)
        self.assertTrue(isinstance(find.rules[0], opsutils._FindNameRule))

    def test_add_rule_directory(self):
        find = opsutils.find('.')
        find._add_rule({'directory': True})
        self.assertEqual(len(find.rules), 1)
        self.assertTrue(isinstance(find.rules[0], opsutils._FindDirectoryRule))

    def test_add_rule_file(self):
        find = opsutils.find('.')
        find._add_rule({'file': True})
        self.assertEqual(len(find.rules), 1)
        self.assertTrue(isinstance(find.rules[0], opsutils._FindFileRule))

    def test_add_rule_time(self):
        find = opsutils.find('.')
        find._add_rule({'atime__year': 2010})
        find._add_rule({'ctime__month': 5})
        find._add_rule({'mtime__day': 1})
        self.assertEqual(len(find.rules), 3)
        self.assertTrue(isinstance(find.rules[0], opsutils._FindTimeRule))
        self.assertTrue(isinstance(find.rules[1], opsutils._FindTimeRule))
        self.assertTrue(isinstance(find.rules[2], opsutils._FindTimeRule))

    def test_filter(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        count = 0
        for path in opsutils.find(dir_path).filter(name='test_find.py'):
            count += 1
        self.assertEqual(count, 1)

    def test_exclude(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        total_count = 0
        exclude_count = 0
        for path in opsutils.find(dir_path):
            total_count += 1
        for path in opsutils.find(dir_path).exclude(name='test_find.py'):
            exclude_count += 1
        self.assertEqual(exclude_count+1, total_count)

if __name__ == '__main__':
    unittest.main()
