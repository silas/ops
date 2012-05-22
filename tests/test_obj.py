import helper

import copy
import unittest
import ops

class ObjTestCase(unittest.TestCase):

    def setUp(self):
        self.o = ops.obj()

    def test_bool_empty(self):
        self.assertFalse(self.o)

    def test_bool_not_empty(self):
        self.o['hello'] = 'world'
        self.assertTrue(self.o)

    def test_bool_false(self):
        self.o['hello'] = 'world'
        self.o._bool = False
        self.assertFalse(self.o)

    def test_bool_true(self):
        self.o._bool = True
        self.assertTrue(self.o)

    def test_default(self):
        o = ops.obj(default='test')
        self.assertEqual(o.fail, 'test')

    def test_dict(self):
        d = {'hello': 'world', 'thanks': 'mom'}
        o = ops.obj(copy.deepcopy(d))
        self.assertEqual(len(o), len(d))
        for key, value in d.items():
            self.assertEqual(o[key], value)
            self.assertEqual(getattr(o, key), value)
        self.assertEqual(unicode(o), unicode(d))
        self.assertEqual(str(o), str(d))

    def test_grow(self):
        self.o.one.two.three.four = 1234
        self.assertEqual(self.o['one']['two']['three']['four'], 1234)
        self.assertEqual(str(self.o), "{'one': {'two': {'three': {'four': 1234}}}}")
        del self.o['one']
        self.o['four']['three']['two']['one'] = 4321
        self.assertEqual(self.o.four.three.two.one, 4321)
        self.assertEqual(str(self.o), "{'four': {'three': {'two': {'one': 4321}}}}")

    def test_grow_false(self):
        try:
            ops.obj(grow=False).fail
            raise Exception("Accessor didn't raise AttributeError.")
        except AttributeError:
            pass

if __name__ == '__main__':
    unittest.main()
