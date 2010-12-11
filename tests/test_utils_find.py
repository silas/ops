import helper

import datetime
import copy
import os
import time
import unittest
import ops.utils

class FindRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = ops.utils._FindRule()

    def test_call(self):
        try:
            self.rule(ops.utils.path('/tmp'))
        except NotImplementedError:
            pass

    def test_render(self):
        self.assertTrue(self.rule.render())
        self.assertFalse(self.rule.render(False))
        rule = ops.utils._FindRule(exclude=True)
        self.assertFalse(rule.render())
        self.assertTrue(rule.render(False))

class FindDirectoryRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = ops.utils._FindDirectoryRule(True)
        self.file_path = ops.utils.path(__file__)

    def test_call(self):
        self.assertFalse(self.rule(self.file_path))

    def test_directory(self):
        path = ops.utils.path(os.path.dirname(self.file_path))
        self.assertTrue(self.rule(path))

class FindFileRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = ops.utils._FindFileRule(True)
        self.file_path = ops.utils.path(__file__)

    def test_file(self):
        self.assertTrue(self.rule(self.file_path))

    def test_directory(self):
        path = ops.utils.path(os.path.dirname(self.file_path))
        self.assertFalse(self.rule(path))

class FindNameRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.rule = ops.utils._FindNameRule('*hello[12].py?')

    def test_match(self):
        self.assertTrue(self.rule(ops.utils.path('hello1.pyc')))
        self.assertTrue(self.rule(ops.utils.path('test-hello2.pyo')))

    def test_no_match(self):
        self.assertFalse(self.rule(ops.utils.path('world.py')))

class FindTimeRuleTestCase(unittest.TestCase):

    def setUp(self):
        self.dt_eq = datetime.datetime(year=2010, month=11, day=12, hour=13, minute=14, second=15)
        self.dt_lt = datetime.datetime(year=2001, month=1, day=2, hour=3, minute=4, second=5)
        self.dt_gt = datetime.datetime(year=2021, month=2, day=3, hour=4, minute=5, second=6)
        p = time.mktime(self.dt_eq.timetuple())
        s = ops.utils.stat('/tmp')
        s._data = [
            0,  # st_mode
            0,  # st_ino
            0,  # st_dev
            1,  # st_nlink
            0,  # st_uid
            0,  # st_gid
            0,  # st_size
            p,  # st_atime
            p,  # st_mtime
            p,  # st_ctime
        ]
        self.path = ops.utils.path('/tmp', stat=s)

    def rule(self, o, v, type='ctime'):
        return ops.utils._FindTimeRule(type, o, v)(self.path)

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

    def setUp(self):
        self.workspace = helper.Workspace()

    def tearDown(self):
        self.workspace.destroy()

    def setup_directory(self):
        for n1 in xrange(0, 3):
            for n2 in xrange(0, 3):
                p = self.workspace.join('dir%s' % n1, 'dir%s' % n2)
                os.makedirs(p)
                with open(os.path.join(p, 'file'), 'w') as f:
                    f.write('hello world')

    def test_add_rule_name(self):
        find = ops.utils.find('.')
        find._add_rule({'name': '*.pyc'})
        self.assertEqual(len(find.rules), 1)
        self.assertTrue(isinstance(find.rules[0], ops.utils._FindNameRule))

    def test_add_rule_directory(self):
        find = ops.utils.find('.')
        find._add_rule({'directory': True})
        self.assertEqual(len(find.rules), 1)
        self.assertTrue(isinstance(find.rules[0], ops.utils._FindDirectoryRule))

    def test_add_rule_file(self):
        find = ops.utils.find('.')
        find._add_rule({'file': True})
        self.assertEqual(len(find.rules), 1)
        self.assertTrue(isinstance(find.rules[0], ops.utils._FindFileRule))

    def test_add_rule_time(self):
        find = ops.utils.find('.')
        find._add_rule({'atime__year': 2010})
        find._add_rule({'ctime__month': 5})
        find._add_rule({'mtime__day': 1})
        self.assertEqual(len(find.rules), 3)
        self.assertTrue(isinstance(find.rules[0], ops.utils._FindTimeRule))
        self.assertTrue(isinstance(find.rules[1], ops.utils._FindTimeRule))
        self.assertTrue(isinstance(find.rules[2], ops.utils._FindTimeRule))

    def test_filter(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        count = 0
        for path in ops.utils.find(dir_path).filter(name='test_utils_find.py'):
            count += 1
        self.assertEqual(count, 1)

    def test_exclude(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        total_count = 0
        exclude_count = 0
        for path in ops.utils.find(dir_path):
            total_count += 1
        for path in ops.utils.find(dir_path).exclude(name='test_utils_find.py'):
            exclude_count += 1
        self.assertEqual(exclude_count+1, total_count)

    def test_top_down(self):
        self.setup_directory()

        list1 = list(ops.utils.find(self.workspace.path))
        list2 = list(ops.utils.find(self.workspace.path, top_down=True))
        list3 = list(ops.utils.find(self.workspace.path, no_peek=True, top_down=True))

        self.assertEqual(len(list1), 22)
        self.assertEqual(len(list2), len(list1))
        self.assertEqual(len(list3), len(list2))

        self.assertNotEqual(list2[0], list1[0])
        self.assertNotEqual(list2[-1], list1[-1])

        for i, v in enumerate(list2):
            self.assertEqual(list3[i], v)

        list1.sort()
        list2.sort()
        for i, v in enumerate(list1):
            self.assertEqual(list2[i], v)

if __name__ == '__main__':
    unittest.main()
