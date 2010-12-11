import helper

import copy
import unittest
import ops.utils

class ObjectifyTestCase(unittest.TestCase):

    def setUp(self):
        self.o = ops.utils.objectify()

    def test_bool_empty(self):
        self.assertFalse(self.o)

    def test_bool_not_empty(self):
        self.o['hello'] = 'world'
        self.assertTrue(self.o)

    def test_bool_false(self):
        self.o['hello'] = 'world'
        self.o['_bool'] = False
        self.assertFalse(self.o)

    def test_bool_true(self):
        self.o['_bool'] = True
        self.assertTrue(self.o)

    def test_default(self):
        try:
            self.o.fail
            raise Exception("Accessor didn't raise AttributeError.")
        except AttributeError:
            pass
        o = ops.utils.objectify(default='test')
        self.assertEqual(o.fail, 'test')

    def test_dict(self):
        d = {'hello': 'world', 'thanks': 'mom'}
        o = ops.utils.objectify(copy.deepcopy(d))
        self.assertEqual(len(o), len(d))
        for key, value in d.items():
            self.assertEqual(o[key], value)
            self.assertEqual(getattr(o, key), value)
        self.assertEqual(unicode(o), unicode(d))
        self.assertEqual(str(o), str(d))

if __name__ == '__main__':
    unittest.main()
